#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import itertools
import re

from nltk import sent_tokenize
from pynlpl.clients.frogclient import FrogClient
from pattern.nl import sentiment

from newsgac import config
from newsgac.caches.models import Cache
from newsgac.common.utils import split_long_sentences, split_chunks
import newsgac.data_engineering.utils as Utilities

def clean_ocr_errors(ocr):

    # Remove unwanted characters
    unwanted_chars = [u'|', u'_', u'=', u'(', u')', u'[', u']', u'<',
                      u'>', u'#', u'/', u'\\', u'*', u'~', u'`', u'«', u'»', u'®', u'^',
                      u'°', u'•', u'★', u'■', u'{', u'}']
    for char in unwanted_chars:
        ocr = ocr.replace(char, '')
        ocr = ' '.join(ocr.split())

    return ocr

def get_frog_tokens(text):
    cache = Cache.get_or_new(hashlib.sha1(text.encode('utf-8')).hexdigest())
    if not cache.data:
        sentences = [s for s in sent_tokenize(text) if s]
        num_sentences = len(sentences)
        sentences = split_long_sentences(sentences, 48)
        chunks = [' '.join(chunk).encode('utf-8') for chunk in split_chunks(sentences, 10)]

        frogclient = FrogClient(config.frog_hostname, config.frog_port, returnall=True)
        tokens = itertools.chain.from_iterable([frogclient.process(chunk) for chunk in chunks])
        token_list = [token for token in tokens if None not in token]
        cache.data={}
        cache.data['tokens'] = token_list
        cache.data['num_sentences'] = num_sentences
        cache.save()
    return cache.data


def get_frog_features(text):
    features = {}

    # Clean ocr errors
    clean_text = clean_ocr_errors(text)

    # Split frog processing into direct quotes and text free from direct quotes
    # Find quoted text
    # todo: regex needs extensive testing, this is not reliable and captures apostrophes
    quotes = re.findall(r"\'(.+?)\'", clean_text)
    quote_free_text, nr_subs1 = re.subn(r"\'(.+?)\'", ' ', clean_text)
    quotes.append(re.findall(r"\"(.+?)\"", quote_free_text))
    quote_free_text, nr_subs2 = re.subn(r"\"(.+?)\"", ' ', quote_free_text)
    quotes.append(re.findall(r"”(.+?)”", quote_free_text))
    quote_free_text, nr_subs3 = re.subn(r"”(.+?)”", ' ', quote_free_text)
    quotes.append(re.findall(r"„(.+?)”", quote_free_text))
    quote_free_text, nr_subs4 = re.subn(r"„(.+?)”", ' ', quote_free_text)
    quotes.append(re.findall(r"„(.+?)\'\'", quote_free_text))
    quote_free_text, nr_subs5 = re.subn(r"„(.+?)\'\'", ' ', quote_free_text)

    quotes_text = ''
    for quote in quotes:
        if quote:
            quotes_text += quote.strip() + '. '

    quote_free_text = ' '.join(quote_free_text.split())
    # Direct quotes
    features['direct_quotes'] = nr_subs1 + nr_subs2 + nr_subs3 + nr_subs4 + nr_subs5

    # process quotes with frog
    quotes_data_dict = get_frog_tokens(quotes_text)
    quote_tokens = quotes_data_dict['tokens']
    num_quotes = quotes_data_dict['num_sentences']

    # process quote free text with frog
    data_dict = get_frog_tokens(quote_free_text)
    tokens = data_dict['tokens']
    num_sentences = data_dict['num_sentences']

    # Direct quotes percentage wrt quote free text sentence count
    features['direct_quotes_perc'] = float(num_quotes) / float(num_sentences)

    # Sentence count for quote free text
    features['sentences'] = num_sentences

    # Token count
    token_count = len(tokens)

    # Average sentence length
    features['avg_sentence_length'] = (token_count / float(num_sentences)) if num_sentences > 0 else 0

    # Count punctuation
    qm_count = quote_free_text.count('?')
    features['question_marks_perc'] = qm_count / float(token_count)
    em_count = quote_free_text.count('!')
    features['exclamation_marks_perc'] = em_count / float(token_count)
    currency_symbols = 0
    for char in [u'$', u'€', u'£', u'ƒ']:
        currency_symbols += quote_free_text.count(char)
    features['currency_symbols_perc'] = currency_symbols / float(token_count)
    digit_count = len([c for c in quote_free_text if c.isdigit()])
    features['digits_perc'] = digit_count / float(token_count)

    # Numbers
    num_count = len([t for t in tokens if t[4].startswith('TW')])
    features['number_perc'] = (num_count / float(token_count)) if float(token_count) > 0 else 0

    # Adjective count and percentage
    adj_count = len([t for t in tokens if t[4].startswith('ADJ')])
    features['adjectives_perc'] = (adj_count / float(token_count)) if float(token_count) > 0 else 0

    # Verbs and adverbs count and percentage
    modal_verb = [t for t in tokens if t[4].startswith('WW') and
                  t[2].capitalize() in Utilities.modal_verbs]
    modal_verb_count = len(modal_verb)
    features['modal_verbs_perc'] = (modal_verb_count / float(token_count)) if float(token_count) > 0 else 0

    modal_adverb_count = len([t for t in tokens if t[4].startswith('BW')
                              and t[2].capitalize() in Utilities.modal_adverbs])
    features['modal_adverbs_perc'] = (modal_adverb_count /
                                      float(token_count)) if float(token_count) > 0 else 0

    cogn_verb_count = len([t for t in tokens if t[4].startswith('WW') and
                           t[2].capitalize() in Utilities.cogn_verbs])
    features['cogn_verbs_perc'] = (cogn_verb_count / float(token_count)) if float(token_count) > 0 else 0

    intensifier_count = len([t for t in tokens if t[2].capitalize() in
                             Utilities.intensifiers])
    features['intensifiers_perc'] = (intensifier_count / float(token_count)) if float(token_count) > 0 else 0

    # Personal pronoun counts and percentages
    pronoun_1_count = len([t for t in tokens if t[4].startswith('VNW') and
                           t[2] in Utilities.pronouns_1])
    pronoun_1_count_wdq = pronoun_1_count + len([t for t in quote_tokens if t[4].startswith('VNW') and
                                                t[2] in Utilities.pronouns_1])
    pronoun_2_count = len([t for t in tokens if t[4].startswith('VNW') and
                           t[2] in Utilities.pronouns_2])
    pronoun_2_count_wdq = pronoun_2_count + len([t for t in quote_tokens if t[4].startswith('VNW') and
                                                 t[2] in Utilities.pronouns_2])
    pronoun_3_count = len([t for t in tokens if t[4].startswith('VNW') and
                           t[2] in Utilities.pronouns_3])

    features['pronoun_1_perc'] = (pronoun_1_count / float(token_count)) if float(token_count) > 0 else 0
    features['pronoun_2_perc'] = (pronoun_2_count / float(token_count)) if float(token_count) > 0 else 0
    features['pronoun_3_perc'] = (pronoun_3_count / float(token_count)) if float(token_count) > 0 else 0

    features['pronoun_1_perc_wdq'] = (pronoun_1_count_wdq / float(token_count)) if float(token_count) > 0 else 0
    features['pronoun_2_perc_wdq'] = (pronoun_2_count_wdq / float(token_count)) if float(token_count) > 0 else 0

    # Named entities
    named_entities = [t for t in tokens if t[5].startswith('B')]

    features['named_entities_perc'] = (len(named_entities) /
                                       float(token_count)) if float(token_count) > 0 else 0

    # Unique named entities
    unique_ne_strings = []
    ne_strings = set([t[1].lower() for t in named_entities])
    for ne_source in ne_strings:
        unique = True
        for ne_target in [n for n in ne_strings if n != ne_source]:
            if ne_target.find(ne_source) > -1:
                unique = False
                break
        if unique:
            unique_ne_strings.append(ne_source)

    features['unique_named_entities'] = (len(unique_ne_strings) /
                                         float(len(named_entities))) if len(named_entities) else 0


    polarity, subjectivity = sentiment(text)
    features['polarity'] = polarity
    features['subjectivity'] = subjectivity


    return features

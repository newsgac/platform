#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' This class encapsulates the feature extraction techniques, such as
stylistic features (e.g. frequency of particular punctuation), morphological features (e.g. average length of the words), etc
'''
# Genre Classifier
#
# Copyright (C) 2016 Juliette Lonij, Koninklijke Bibliotheek -
# National Library of the Netherlands
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals
import re
import time
import urllib
import numpy as np
from sklearn.externals.joblib import Parallel
from sklearn.externals.joblib import delayed
from scipy import sparse
import src.data_engineering.utils as Utilities
from collections import OrderedDict
from lxml import etree
# from segtok import segmenter
from nltk.tokenize import sent_tokenize
from sklearn.base import BaseEstimator, TransformerMixin
import spacy
# import frog
# frog_nl = frog.Frog(frog.FrogOptions(parser=False))
from pynlpl.clients.frogclient import FrogClient
port = 12345
# frogclient = FrogClient('localhost',port, returnall=True)
connected = False
while not connected:
    try:
        frogclient = FrogClient('frog',port, returnall=True)        # use this when dockerized
        connected = True
    except e:
        connected = False

class ArticleTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, url=None, text=None, preprocessor=None):
        self.art = Article(text=text)
        self.preprocessor = preprocessor

    def fit(self, X, y):
        return None

    def transform(self, X):
        self.X = X
        # count = 0
        # results = []
        # for x in X:
        #     print count
        #     new_art = Article(text=x)
        #     new_art.get_features_spacy()
        #     print new_art.features.values()
        #     res = np.reshape(new_art.features.values(), (1, len(new_art.features.values())))
        #     print "Result reshaped ", res
        #     results.append(res)
        #     count += 1
        # print "Article Transformer : ", results
        # return np.array(results)

        Xs = Parallel(n_jobs=50)(
            delayed(_transform_one)(x, self.preprocessor) for x in self.X if len(x)>10)
        if not Xs:
            # All transformers are None
            return np.zeros((X.shape[0], 0))
        if any(sparse.issparse(f) for f in Xs):
            # Xs = sparse.hstack(Xs).tocsr()
            Xs = sparse.vstack(Xs).tocsr()
        else:
            # Xs = np.hstack(Xs)
            Xs = np.vstack(Xs)
        return Xs

def _transform_one(x, preprocessor):
    from src.data_engineering.preprocessing import process_raw_text_for_config
    processed_text, features, id = process_raw_text_for_config(preprocessor, x)
    # new_art = Article(text=x)
    # new_art.get_features_spacy()
    sorted_keys = sorted(features.keys())
    import src.models.data_sources.constants as DataSourceConstants
    ordered_feature_values = [features[f] for f in sorted_keys if
                              f not in DataSourceConstants.NON_FEATURE_COLUMNS]
    res = np.reshape(ordered_feature_values, (1, len(ordered_feature_values)))
    return res


class Article(object):
    '''
    A newspaper article to be classified.
    '''

    def __init__(self, url=None, text=None):
        '''
        Set article attributes.
        '''
        self.url = url
        self.text = text
        self.features = {}

    def get_features_frog(self):
        '''
        Calculate article features.
        '''
        features = {}

        # Get article OCR
        if self.url:
            ocr = self.get_ocr(self.url)
        elif self.text:
            if type(self.text) is list:
                ocr = self.text[0]
            else:
                ocr = self.text

        # Remove unwanted characters
        unwanted_chars = [u'|', u'_', u'=', u'(', u')', u'[', u']', u'<',
            u'>', u'#', u'/', u'\\', u'*', u'~', u'`', u'«', u'»', u'®', u'^',
            u'°', u'•', u'★', u'■', u'{', u'}']
        for char in unwanted_chars:
            ocr = ocr.replace(char, '')
            ocr = ' '.join(ocr.split())

        # Find and remove quoted text
        opening_quote_chars = [u'„', u'‚‚', u',,']
        closing_quote_chars = [u'"', u'”', u"'", u'’']

        pattern = ('(^|[^\w])(' + '|'.join(opening_quote_chars +
            closing_quote_chars) + ')(\s\w|\w\w)')
        pattern += ('(?:(?!' + '|'.join(opening_quote_chars +
            ['\s' + c + '\w\w' for c in closing_quote_chars]) +
            ').){0,1000}?')
        pattern += '(' + '|'.join(closing_quote_chars) + ')($|[^\w])'
        pattern = re.compile(pattern, flags=re.UNICODE|re.DOTALL)

        clean_ocr, nr_subs = re.subn(pattern, '', ocr)
        clean_ocr = ' '.join(clean_ocr.split())
        features['direct_quotes'] = nr_subs

        # Count remaining quote chars
        rem_quote_chars = 0
        for char in opening_quote_chars + closing_quote_chars:
            rem_quote_chars += clean_ocr.count(char)
        features['remaining_quote_chars'] = rem_quote_chars

        # Count punctuation
        features['question_marks'] = clean_ocr.count('?')
        features['question_marks_perc'] = (clean_ocr.count('?') /
            float(len(clean_ocr)))
        features['exclamation_marks'] = clean_ocr.count('!')
        features['exclamation_marks_perc'] = (clean_ocr.count('!') /
            float(len(clean_ocr)))
        currency_symbols = 0
        for char in [u'$', u'€', u'£', u'ƒ']:
            currency_symbols += clean_ocr.count(char)
        features['currency_symbols'] = currency_symbols
        features['currency_symbols_perc'] = (currency_symbols /
            float(len(clean_ocr)))
        features['digits'] = len([c for c in clean_ocr if c.isdigit()])
        features['digits_perc'] = (len([c for c in clean_ocr if c.isdigit()]) /
            float(len(clean_ocr)))

        # Sentence chunk cleaned OCR with Segtok
        # sentences = [s for s in segmenter.split_single(clean_ocr) if s]
        sentences = [s for s in sent_tokenize(clean_ocr) if s]
        sentence_count = len(sentences)
        features['sentences'] = sentence_count


        # Chunk, tokenize, tag, lemmatize with Frog
        tokens = self.frog(sentences)

        # Word count
        token_count = len(tokens)
        features['tokens'] = token_count
        features['avg_sentence_length'] = (token_count / sentence_count) if sentence_count > 0 else 0

        # Adjective count and percentage
        adj_count = len([t for t in tokens if t[4].startswith('ADJ')])
        features['adjectives'] = adj_count
        features['adjectives_perc'] = (adj_count / float(token_count)) if float(token_count) > 0 else 0

        # Verbs and adverbs count and percentage
        modal_verb = [t for t in tokens if t[4].startswith('WW') and
                                t[2].capitalize() in Utilities.modal_verbs]
        modal_verb_count = len(modal_verb)
        features['modal_verbs'] = modal_verb_count
        features['modal_verbs_perc'] = (modal_verb_count / float(token_count)) if float(token_count) > 0 else 0

        modal_adverb_count = len([t for t in tokens if t[4].startswith('BW')
            and t[2].capitalize() in Utilities.modal_adverbs])
        features['modal_adverbs'] = modal_adverb_count
        features['modal_adverbs_perc'] = (modal_adverb_count /
            float(token_count)) if float(token_count) > 0 else 0

        cogn_verb_count = len([t for t in tokens if t[4].startswith('WW') and
            t[2].capitalize() in Utilities.cogn_verbs])
        features['cogn_verbs'] = cogn_verb_count
        features['cogn_verbs_perc'] = (cogn_verb_count / float(token_count)) if float(token_count) > 0 else 0

        intensifier_count = len([t for t in tokens if t[2].capitalize() in
            Utilities.intensifiers])
        features['intensifiers'] = intensifier_count
        features['intensifiers_perc'] = (intensifier_count / float(token_count)) if float(token_count) > 0 else 0

        # Personal pronoun counts and percentages
        pronoun_1_count = len([t for t in tokens if t[4].startswith('VNW') and
            t[2] in Utilities.pronouns_1])
        pronoun_2_count = len([t for t in tokens if t[4].startswith('VNW') and
            t[2] in Utilities.pronouns_2])
        pronoun_3_count = len([t for t in tokens if t[4].startswith('VNW') and
            t[2] in Utilities.pronouns_3])
        pronoun_count = pronoun_1_count + pronoun_2_count + pronoun_3_count

        features['pronoun_1'] = pronoun_1_count
        features['pronoun_2'] = pronoun_2_count
        features['pronoun_3'] = pronoun_3_count
        features['pronoun_1_perc'] = (pronoun_1_count / float(token_count)) if float(token_count) > 0 else 0
        features['pronoun_2_perc'] = (pronoun_2_count / float(token_count)) if float(token_count) > 0 else 0
        features['pronoun_3_perc'] = (pronoun_3_count / float(token_count)) if float(token_count) > 0 else 0
        features['pronoun_1_perc_rel'] = (pronoun_1_count / float(pronoun_count)
            if pronoun_count > 0 else 0)
        features['pronoun_2_perc_rel'] = (pronoun_2_count / float(pronoun_count)
            if pronoun_count > 0 else 0)
        features['pronoun_3_perc_rel'] = (pronoun_3_count / float(pronoun_count)
            if pronoun_count > 0 else 0)

        # Named entities
        named_entities = [t for t in tokens if t[5].startswith('B')]

        # NE count
        features['named_entities'] = len(named_entities)
        features['named_entities_perc'] = (len(named_entities) /
            float(token_count)) if float(token_count) > 0 else 0

        # NE position
        features['named_entities_pos'] = ((sum([tokens.index(t) for t in
            named_entities]) / float(len(named_entities))) /
            float(token_count)) if len(named_entities) and token_count > 0 else 0

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

        # Self classification
        # lemmas = [t[2].lower() for t in tokens]
        # for cl in Utilities.self_classifications:
        #     feature_name = 'self_cl_' + cl
        #     features[feature_name] = 0
        #     for w in Utilities.self_classifications[cl]:
        #         if w in lemmas:
        #             features[feature_name] += 1

        #New features
        self.add_common_features(self.text, features)

        self.features = OrderedDict(sorted(features.items(), key=lambda t: t[0]))
        return self.features

    def add_common_features(self, text, features):

        from pattern.nl import sentiment
        polarity, subjectivity = sentiment(text)
        features['polarity'] = polarity
        features['subjectivity'] = subjectivity
        count_past = 0
        count_pres = 0
        # prevailing tense in ADJ, VERB
        # for token in tokens:
        #     if "Tense=Past" in token.tag_:
        #         count_past += 1
        #     elif "Tense=Pres" in token.tag_:
        #         count_pres += 1
        # if count_past > count_pres:
        #     # PAST TENSE
        #     features['prevailing_tense'] = -1
        # elif count_past < count_pres:
        #     # PRESENT TENSE
        #     features['prevailing_tense'] = 1
        # else:
        #     features['prevailing_tense'] = 0

    def get_features_spacy(self):
        spacy_nl = spacy.load('nl')
        '''
        Calculate article features.
        '''
        features = {}

        # Get article OCR
        if self.url:
            ocr = self.get_ocr(self.url)
        elif self.text:
            ocr = self.text

        # Remove unwanted characters
        unwanted_chars = [u'|', u'_', u'=', u'(', u')', u'[', u']', u'<',
            u'>', u'#', u'/', u'\\', u'*', u'~', u'`', u'«', u'»', u'®', u'^',
            u'°', u'•', u'★', u'■', u'{', u'}']
        for char in unwanted_chars:
            ocr = ocr.replace(char, '')
            ocr = ' '.join(ocr.split())

        # Find and remove quoted text
        opening_quote_chars = [u'„', u'‚‚', u',,']
        closing_quote_chars = [u'"', u'”', u"'", u'’']

        pattern = ('(^|[^\w])(' + '|'.join(opening_quote_chars +
            closing_quote_chars) + ')(\s\w|\w\w)')
        pattern += ('(?:(?!' + '|'.join(opening_quote_chars +
            ['\s' + c + '\w\w' for c in closing_quote_chars]) +
            ').){0,1000}?')
        pattern += '(' + '|'.join(closing_quote_chars) + ')($|[^\w])'
        pattern = re.compile(pattern, flags=re.UNICODE|re.DOTALL)

        clean_ocr, nr_subs = re.subn(pattern, '', ocr)
        clean_ocr = ' '.join(clean_ocr.split())
        features['direct_quotes'] = nr_subs

        # Count remaining quote chars
        rem_quote_chars = 0
        for char in opening_quote_chars + closing_quote_chars:
            rem_quote_chars += clean_ocr.count(char)
        features['remaining_quote_chars'] = rem_quote_chars

        # Count punctuation
        features['question_marks'] = clean_ocr.count('?')
        features['question_marks_perc'] = (clean_ocr.count('?') /
            float(len(clean_ocr)))
        features['exclamation_marks'] = clean_ocr.count('!')
        features['exclamation_marks_perc'] = (clean_ocr.count('!') /
            float(len(clean_ocr)))
        currency_symbols = 0
        for char in [u'$', u'€', u'£', u'ƒ']:
            currency_symbols += clean_ocr.count(char)
        features['currency_symbols'] = currency_symbols
        features['currency_symbols_perc'] = (currency_symbols /
            float(len(clean_ocr)))
        features['digits'] = len([c for c in clean_ocr if c.isdigit()])
        features['digits_perc'] = (len([c for c in clean_ocr if c.isdigit()]) /
            float(len(clean_ocr)))

        # Sentence chunk cleaned OCR with Segtok
        # sentences = [s for s in segmenter.split_single(clean_ocr) if s]
        sentences = [s for s in sent_tokenize(clean_ocr) if s]
        sentence_count = len(sentences)
        features['sentences'] = sentence_count

        # Chunk, tokenize, tag, lemmatize with Spacy
        tokens = []
        doc = spacy_nl(self.text)
        named_entities = [t.text for t in doc.ents]
        for token in doc:
            if token.text in named_entities:
                tokens.append([token.text, token.pos_, token.lemma_, token.tag_, "NE"])
            else:
                tokens.append([token.text, token.pos_, token.lemma_, token.tag_, "NNE"])

        # Word count
        token_count = len(tokens)
        features['tokens'] = token_count
        features['avg_sentence_length'] = token_count / sentence_count

        # Adjective count and percentage
        adj_count = len([t for t in tokens if t[1].startswith('ADJ')])
        features['adjectives'] = adj_count
        features['adjectives_perc'] = adj_count / float(token_count)

        # Verbs and adverbs count and percentage
        # look at the lemma
        modal_verb = [t for t in tokens if t[1].startswith('VERB') and
                      t[2].capitalize() in Utilities.modal_verbs]
        modal_verb_count = len(modal_verb)
        features['modal_verbs'] = modal_verb_count
        features['modal_verbs_perc'] = modal_verb_count / float(token_count)

        modal_adverb_count = len([t for t in tokens if t[1].startswith('ADV')
            and t[2].capitalize() in Utilities.modal_adverbs])
        features['modal_adverbs'] = modal_adverb_count
        features['modal_adverbs_perc'] = (modal_adverb_count /
            float(token_count))

        cogn_verb_count = len([t for t in tokens if t[1].startswith('VERB') and
            t[2].capitalize() in Utilities.cogn_verbs])
        features['cogn_verbs'] = cogn_verb_count
        features['cogn_verbs_perc'] = cogn_verb_count / float(token_count)

        intensifier_count = len([t for t in tokens if t[0].capitalize() in
            Utilities.intensifiers])
        features['intensifiers'] = intensifier_count
        features['intensifiers_perc'] = intensifier_count / float(token_count)

        # Personal pronoun counts and percentages
        pronoun_1_count = len([t for t in tokens if t[1].startswith('PRON') and
            t[0].lower() in Utilities.pronouns_1])
        pronoun_2_count = len([t for t in tokens if t[1].startswith('PRON') and
            t[0].lower() in Utilities.pronouns_2])
        pronoun_3_count = len([t for t in tokens if t[1].startswith('PRON') and
            t[0].lower() in Utilities.pronouns_3])
        pronoun_count = pronoun_1_count + pronoun_2_count + pronoun_3_count

        features['pronoun_1'] = pronoun_1_count
        features['pronoun_2'] = pronoun_2_count
        features['pronoun_3'] = pronoun_3_count
        features['pronoun_1_perc'] = pronoun_1_count / float(token_count)
        features['pronoun_2_perc'] = pronoun_2_count / float(token_count)
        features['pronoun_3_perc'] = pronoun_3_count / float(token_count)
        features['pronoun_1_perc_rel'] = (pronoun_1_count / float(pronoun_count)
            if pronoun_count > 0 else 0)
        features['pronoun_2_perc_rel'] = (pronoun_2_count / float(pronoun_count)
            if pronoun_count > 0 else 0)
        features['pronoun_3_perc_rel'] = (pronoun_3_count / float(pronoun_count)
            if pronoun_count > 0 else 0)

        # Named entities
        named_entities = [t.text for t in doc.ents]

        # NE count
        features['named_entities'] = len(named_entities)
        features['named_entities_perc'] = (len(named_entities) /
            float(token_count))

        # NE position
        features['named_entities_pos'] = ((sum([idx+1 for idx,t in
                enumerate(tokens) if t[4]=='NE']) / float(len(named_entities))) /
                float(token_count)) if len(named_entities) and token_count > 0 else 0

        # Unique named entities
        unique_ne_strings = []
        ne_strings = set([t[0].lower() for t in named_entities])
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

        # Self classification
        # lemmas = [t[2].lower() for t in tokens]
        # for cl in Utilities.self_classifications:
        #     feature_name = 'self_cl_' + cl
        #     features[feature_name] = 0
        #     for w in Utilities.self_classifications[cl]:
        #         if w in lemmas:
        #             features[feature_name] += 1

        #New features
        self.add_common_features(self.text, features)

        self.features = OrderedDict(sorted(features.items(), key=lambda t: t[0]))
        return self.features

    def get_ocr(self, url):
        '''
        Get article OCR from provide URL.
        '''
        ocr = ''
        while not ocr:
            data = urllib.urlopen(self.url).read()
            data = data.replace('</title>', '.</title>')
            xml = etree.fromstring(data)
            ocr = etree.tostring(xml, encoding='utf8',
                method='text').decode('utf-8')
            if not ocr:
                time.sleep(5)
                print('OCR not found, retrying ...')
        print('OCR found: ' + ' '.join(ocr.split())[:50] + ' ...')
        return ocr

    def frog(self, sentences):

        '''
        Analyze text with Frog NLP suite.
        '''
        # tokens = []
        tokens_new = []
        to_frog = sentences
        while len(to_frog):
            batch_size = 10 if len(to_frog) >= 10 else len(to_frog)
            batch = ' '.join(to_frog[:batch_size]).encode('utf-8')

            # data = ''
            data_new = []
            i = 0
            while not data_new:
                # data = frog_nl.process_raw(batch)

                data_new = frogclient.process(batch)

                # data = data.decode('utf-8')

            # usage with frog_nl
            # lines = [l.split('\t') for l in data.split('\n') if l]
            # tokens += [l for l in lines if len(l) == 10]
            for d in data_new:
                if None not in d:
                    d = ('',) + d       # tackle with the index change diff between local FROG to FROG server in docker
                    tokens_new.append(d)

            to_frog = to_frog[batch_size:]

        return tokens_new

    def frog_log(self, message):
        '''
        Log Frog processing errors.
        '''
        with open('frog_log.txt', 'a') as f:
            # f.write(self.url + ' | ' + message + '\n')
            f.write(message + '\n')
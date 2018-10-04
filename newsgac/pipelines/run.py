#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import re
from sklearn.externals.joblib import delayed

from parallel_with_progress import ParallelWithProgress
from pipelines.data_engineering.preprocessing import remove_stop_words, apply_lemmatization

n_parallel_jobs = 8


def apply_function(function):
    def apply(article):
        article.text = function(article.text)
    return apply

def remove_stop_words_in_article(article):
    article.text = remove_stop_words(article.text)


def apply_lemmatization_in_article(article):
    article.text = apply_lemmatization(article.text)

def get_clean_ocr(ocr):

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
    pattern = re.compile(pattern, flags=re.UNICODE | re.DOTALL)
    clean_ocr, nr_subs = re.subn(pattern, '', ocr)
    # this function was duplicated two-three times, but sometimes with a space:
    #clean_ocr, nr_subs = re.subn(pattern, ' ', ocr)
    clean_ocr = ' '.join(clean_ocr.split())

    return clean_ocr

    # def frog(self, sentences):
    #
    #     '''
    #     Analyze text with Frog NLP suite.
    #     '''
    #     # tokens = []
    #     tokens_new = []
    #     to_frog = sentences
    #     while len(to_frog):
    #         batch_size = 10 if len(to_frog) >= 10 else len(to_frog)
    #         batch = ' '.join(to_frog[:batch_size]).encode('utf-8')
    #
    #         # data = ''
    #         data_new = []
    #         i = 0
    #         while not data_new:
    #             # data = frog_nl.process_raw(batch)
    #             frogclient = FrogClient(config.frog_hostname, config.frog_port, returnall=True)
    #             data_new = frogclient.process(batch)
    #
    #             # data = data.decode('utf-8')
    #
    #         # usage with frog_nl
    #         # lines = [l.split('\t') for l in data.split('\n') if l]
    #         # tokens += [l for l in lines if len(l) == 10]
    #         for d in data_new:
    #             if None not in d:
    #                 d = ('',) + d       # tackle with the index change diff between local FROG to FROG server in docker
    #                 tokens_new.append(d)
    #
    #         to_frog = to_frog[batch_size:]
    #
    #     return tokens_new





def run_pipeline(pipeline):
    articles = pipeline.data_source.articles
    for article in articles:
        article.text = article.raw_text

    if pipeline.sw_removal:
        ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
            delayed(remove_stop_words_in_article)(a) for a in articles
        )

    if pipeline.lemmatization:
        ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
            delayed(apply_lemmatization_in_article)(a) for a in articles
        )

    if pipeline.nlp_tool:
        pass
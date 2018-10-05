#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import re

from nltk import sent_tokenize
from sklearn.externals.joblib import delayed

from common.json_encoder import _dumps
from nlp_tools import Frog
from parallel_with_progress import ParallelWithProgress
import hashlib
from pipelines.data_engineering.preprocessing import remove_stop_words, apply_lemmatization

n_parallel_jobs = 8


def apply_function(function):
    def apply(article):
        article['text'] = function(article['text'])
    return apply

def remove_stop_words_in_article(article):
    article['text'] = remove_stop_words(article['text'])


def apply_lemmatization_in_article(article):
    article['text'] = apply_lemmatization(article['text'])


def apply_nlp_in_article(nlp_tool, article):
    article['features'] = nlp_tool.get_features(article['text'])

# def apply_clean_ocr(article):
#     article['text'] = get_clean_ocr(article['text'])






def apply_tokenize(text):
    return


def run_pipeline(pipeline):
    articles = [
        {
            'index': index,
            'text': article.raw_text
        } for index, article in enumerate(pipeline.data_source.articles)]

    pipeline_dict = pipeline.to_son().to_dict()
    pipeline_cache_repr = {
        'nlp_tool': pipeline_dict['nlp_tool'],
        'sw_removal': pipeline_dict['sw_removal'],
        'lemmatization': pipeline_dict['lemmatization']
    }
    pipeline_cache_hash = hashlib.sha1(_dumps(pipeline_cache_repr)).hexdigest()

    # ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
    #     delayed(apply_clean_ocr)(a) for a in articles
    # )

    # if pipeline.sw_removal:
    #     ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
    #         delayed(remove_stop_words_in_article)(a) for a in articles
    #     )
    #
    # if pipeline.lemmatization:
    #     ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
    #         delayed(apply_lemmatization_in_article)(a) for a in articles
    #     )
    #
    # if pipeline.nlp_tool:
    #     ParallelWithProgress(n_jobs=1, progress_callback=None)(
    #         delayed(apply_nlp_in_article)(pipeline.nlp_tool, a) for a in articles
    #     )


    pass
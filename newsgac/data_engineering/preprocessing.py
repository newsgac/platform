#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' This class encapsulates the data preprocessing techniques, such as
stop-word removal, stemming, etc. using specified NLP methods.
'''
import re
import os
from nltk.stem.snowball import SnowballStemmer

from newsgac import config

language_filename = os.path.join(config.root_path, 'dutch_stopwords_mod.txt')
stop_words = []
try:
    with open(language_filename, 'rb') as language_file:
        stop_words = [
            line.decode('utf-8').strip() for line in language_file.readlines()
        ]
except:
    raise IOError(
        '{0}" file is unreadable, check your installation.'.format(
            language_filename
        )
    )


def remove_stop_words(text):
    pattern = re.compile(r'\b(' + r'|'.join(stop_words) + r')\b\s*')
    reg_text = pattern.sub('', text)

    return reg_text


def apply_lemmatization(text):
    stemmer = SnowballStemmer('dutch', ignore_stopwords=False)
    stem_text = stemmer.stem(text)

    return stem_text


class DataAnalyser():

    def __init__(self):
        pass

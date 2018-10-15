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
    clean_ocr = ' '.join(clean_ocr.split())

    return clean_ocr


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

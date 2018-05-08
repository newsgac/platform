#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' This class encapsulates the data preprocessing techniques, such as
stop-word removal, stemming, etc. using specified NLP methods.
'''

import src.models.data_sources.constants as DataSourceConstants
from stop_words import get_stop_words
import re
from nltk.stem.snowball import SnowballStemmer
from sklearn.externals.joblib import Parallel
from sklearn.externals.joblib import delayed
import src.data_engineering.feature_extraction as FE


class Preprocessor():

    def __init__(self, config=None):
        self.config = config
        if config:
            if 'auto' not in self.config.keys():
                #update defaults
                self.sw_removal = self.config['sw_removal'] if 'sw_removal' in self.config.keys() else DataSourceConstants.DEFAULT_SW_REMOVAL
                self.lemmatization = self.config['lemmatization'] if 'lemmatization' in self.config.keys() else DataSourceConstants.DEFAULT_LEMMA
                self.nlp_tool = self.config['nlp_tool'] if 'nlp_tool' in self.config.keys() else DataSourceConstants.DEFAULT_NLP_TOOL
                self.scaling = self.config['scaling'] if 'scaling' in self.config.keys() else DataSourceConstants.DEFAULT_SCALING
            else:
                self.sw_removal = DataSourceConstants.DEFAULT_SW_REMOVAL
                self.lemmatization = DataSourceConstants.DEFAULT_LEMMA
                self.nlp_tool = DataSourceConstants.DEFAULT_NLP_TOOL
                self.scaling = DataSourceConstants.DEFAULT_SCALING

    def do_parallel_processing(self, documents):

        processed_text_list = []
        feature_list = []
        article_ids = []
        if self.nlp_tool == 'frog':
            # Frog does not work with parallelization
            for processed_text, feature, id in Parallel(n_jobs=1)(
                    delayed(process_raw_text_for_config)(self, d['article_raw_text'], d['_id']) for d in documents):
                article_ids.append(id)
                processed_text_list.append(processed_text)
                feature_list.append(feature)
        elif self.nlp_tool == 'spacy':
            for processed_text, feature, id in Parallel(n_jobs=50)(
                    delayed(process_raw_text_for_config)(self, d['article_raw_text'], d['_id']) for d in documents):
                article_ids.append(id)
                processed_text_list.append(processed_text)
                feature_list.append(feature)

        return article_ids, processed_text_list, feature_list

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

def process_raw_text_for_config(preprocessor, raw_text, id=None):

    # raw_text = raw_text.encode('utf-8')
    processed_text = raw_text.lower()
    features = []

    if preprocessor.sw_removal:
        processed_text = remove_stop_words(processed_text)

    if preprocessor.lemmatization:
        processed_text = apply_lemmatization(processed_text)

    art = FE.Article(text=processed_text)
    if preprocessor.nlp_tool == 'frog':
        features = art.get_features_frog()
    elif preprocessor.nlp_tool == 'spacy':
        features = art.get_features_spacy()

    return processed_text, features, id

def remove_stop_words(text):
    stopwords = get_stop_words('nl')
    pattern = re.compile(r'\b(' + r'|'.join(stopwords) + r')\b\s*')
    reg_text = pattern.sub('', text)

    return reg_text

def apply_lemmatization(text):
    stemmer = SnowballStemmer('dutch', ignore_stopwords=False)
    stem_text = stemmer.stem(text)

    return stem_text


class DataAnalyser():

    def __init__(self):
        pass


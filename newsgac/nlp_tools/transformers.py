#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import numpy
from collections import OrderedDict

from sklearn.base import TransformerMixin
from joblib import delayed, Parallel

from nltk import word_tokenize, sent_tokenize
from nltk.stem.snowball import SnowballStemmer

from newsgac import config

unwanted_chars = {
    '|',
    '_',
    '=',
    '(',
    ')',
    '[',
    ']',
    '<',
    '>',
    '#',
    '/',
    '\\',
    '*',
    '~',
    '`',
    '«',
    '»',
    '®',
    '^',
    '°',
    '•',
    '★',
    '■',
    '{',
    '}',
    '™',
    '§',
    '♦',
    '±',
    '►',
    'и',
    '✓',
    'з',
    '□',
    '▼',
}


class CleanOCR(TransformerMixin):
    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform_text(text):
        for char in unwanted_chars:
            text = text.replace(char, '')
        # gets rid of \t \n
        return ' '.join(text.split())

    def transform(self, X):
        return [CleanOCR.transform_text(text) for text in X]

    def get_params(self, deep=False):
        return {}


class ExtractQuotes(TransformerMixin):
    opening_quote_chars = ['„', '‚‚', ',,']
    closing_quote_chars = ['"', '”', "'", '’']

    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform_text(text):
        opening_quote_chars = ExtractQuotes.opening_quote_chars
        closing_quote_chars = ExtractQuotes.closing_quote_chars

        pattern = ('(' + '|'.join(opening_quote_chars +
                                           closing_quote_chars) + ')(\s\w|\w\w?)')
        pattern += ('(?:(?!' + '|'.join(opening_quote_chars +
                                        ['\s' + c + '\w\w' for c in closing_quote_chars]) +
                    ').){0,1000}?')
        pattern += '(' + '|'.join(closing_quote_chars) + ')($|[^\w])'
        pattern = re.compile(pattern, flags=re.UNICODE | re.DOTALL)
        cleaned_text, nr_subs = re.subn(pattern, '', text)
        return cleaned_text, nr_subs

    def transform(self, X):
        list_nr_subs = []
        for text in X:
            cleaned_text, nr_subs = ExtractQuotes.transform_text(text)
            sentences = [s for s in sent_tokenize(text) if s]
            percentage = float(nr_subs) / len(sentences)
            list_nr_subs.append(numpy.array([percentage]))
        return numpy.array(list_nr_subs)

    @staticmethod
    def get_feature_names():
        return ['direct_quotes_perc']

    def get_params(self, deep=False):
        return {}


class RemoveQuotes(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        texts = []
        for text in X:
            cleaned_text, nr_subs = ExtractQuotes.transform_text(text)
            texts.append(cleaned_text)
        return texts

    def get_params(self, deep=False):
        return {}


class ExtractBasicFeatures(TransformerMixin):
    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform_text(text):
        features = OrderedDict()

        # TODO: these methods introduce inconsistency I think as word_tokenize may return 0
        word_tokens = [w for w in word_tokenize(text) if w]
        sentence_tokens = [s for s in sent_tokenize(text) if s]
        word_token_count = len(word_tokens)
        sentence_token_count = len(sentence_tokens)

        features['question_marks_perc'] = text.count('?') / float(word_token_count) if word_token_count > 0 else 0
        features['exclamation_marks_perc'] = text.count('!') / float(word_token_count) if word_token_count > 0 else 0
        currency_symbols = 0
        for char in ['$', '€', '£', 'ƒ']:
            currency_symbols += text.count(char)
        features['currency_symbols_perc'] = currency_symbols / float(word_token_count) if word_token_count > 0 else 0
        features['digits_perc'] = len([c for c in text if c.isdigit()]) / float(word_token_count) if word_token_count > 0 else 0

        features['sentences'] = len(sentence_tokens)
        features['avg_sentence_length'] = (word_token_count / float(sentence_token_count)) if sentence_token_count > 0 else 0

        return numpy.array([value for idx, value in features.items()])

        # return features

    def transform(self, X):
        return numpy.array([ExtractBasicFeatures.transform_text(text) for text in X])

    def get_params(self, deep=False):
        return {}

    @staticmethod
    def get_feature_names():
        return [
            'question_marks_perc',
            'exclamation_marks_perc',
            'currency_symbols_perc',
            'digits_perc',
            'sentences',
            'avg_sentence_length',
        ]


class ExtractSentimentFeatures(TransformerMixin):
    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform_text(text):
        from pattern.text.nl import sentiment
        polarity, subjectivity = sentiment(text)
        return numpy.array([
            polarity,
            subjectivity
        ])

    def transform(self, X):
        return numpy.array([ExtractSentimentFeatures.transform_text(text) for text in X])

    def get_params(self, deep=False):
        return {}

    @staticmethod
    def get_feature_names():
        return [
            'polarity',
            'subjectivity'
        ]



## STOP WORD REMOVAL
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
    pattern = re.compile(r'\b(' + r'|'.join(stop_words) + r')\b\s*', re.IGNORECASE)
    reg_text = pattern.sub('', text)

    return reg_text



class StopWordRemoval(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return Parallel(n_jobs=config.n_parallel_jobs)(
            delayed(remove_stop_words)(a) for a in X
        )

    def get_params(self, deep=False):
        return {}


class Lowercase(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [text.lower() for text in X]

    def get_params(self, deep=False):
        return {}



## LEMMATIZATION
def apply_lemmatization(text):
    stemmer = SnowballStemmer('dutch', ignore_stopwords=False)
    stem_text = stemmer.stem(text)

    return stem_text

class ApplyLemmatization(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return Parallel(n_jobs=config.n_parallel_jobs)(
            delayed(apply_lemmatization)(a) for a in X
        )

    def get_params(self, deep=False):
        return {}

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

import numpy
from nltk import word_tokenize, sent_tokenize
from sklearn.base import TransformerMixin
from sklearn.externals.joblib import delayed

from newsgac import config
from newsgac.data_engineering.preprocessing import remove_stop_words, apply_lemmatization
from newsgac.parallel_with_progress import ParallelWithProgress


class CleanOCR(TransformerMixin):
    unwanted_chars = [u'|', u'_', u'=', u'(', u')', u'[', u']', u'<',
                      u'>', u'#', u'/', u'\\', u'*', u'~', u'`', u'«', u'»', u'®', u'^',
                      u'°', u'•', u'★', u'■', u'{', u'}']

    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform_text(text):
        for char in CleanOCR.unwanted_chars:
            text = text.replace(char, '')
        return ' '.join(text.split())

    def transform(self, X):
        return [CleanOCR.transform_text(text) for text in X]

    def get_params(self, deep=False):
        return {}


class ExtractQuotes(TransformerMixin):
    opening_quote_chars = [u'„', u'‚‚', u',,']
    closing_quote_chars = [u'"', u'”', u"'", u'’']

    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform_text(text):
        opening_quote_chars = ExtractQuotes.opening_quote_chars
        closing_quote_chars = ExtractQuotes.closing_quote_chars

        pattern = ('(^|[^\w])(' + '|'.join(opening_quote_chars +
                                           closing_quote_chars) + ')(\s\w|\w\w)')
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
            list_nr_subs.append(nr_subs)
        return numpy.array(list_nr_subs)

    def get_feature_names(self):
        return ['direct_quotes']

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
        features = {}
        word_tokens = [w for w in word_tokenize(text) if w]
        sentence_tokens = [s for s in sent_tokenize(text) if s]
        word_token_count = len(word_tokens)
        sentence_token_count = len(sentence_tokens)

        features['question_marks_perc'] = text.count('?') / float(word_token_count)
        features['exclamation_marks_perc'] = text.count('!') / float(word_token_count)
        currency_symbols = 0
        for char in [u'$', u'€', u'£', u'ƒ']:
            currency_symbols += text.count(char)
        features['currency_symbols_perc'] = currency_symbols / float(word_token_count)
        features['digits_perc'] = len([c for c in text if c.isdigit()]) / float(word_token_count)

        features['sentences'] = len(sentence_tokens)
        features['avg_sentence_length'] = (word_token_count / float(sentence_token_count)) if sentence_token_count > 0 else 0
        return features

    def transform(self, X):
        return [ExtractBasicFeatures.transform_text(text) for text in X]

    def get_params(self, deep=False):
        return {}


class ExtractSentimentFeatures(TransformerMixin):
    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform_text(text):
        from pattern.nl import sentiment
        polarity, subjectivity = sentiment(text)
        return {
            'polarity': polarity,
            'subjectivity': subjectivity
        }

    def transform(self, X):
        return [ExtractSentimentFeatures.transform_text(text) for text in X]

    def get_params(self, deep=False):
        return {}


class StopWordRemoval(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return ParallelWithProgress(n_jobs=config.n_parallel_jobs, progress_callback=None)(
            delayed(remove_stop_words)(a) for a in X
        )

    def get_params(self, deep=False):
        return {}


class ApplyLemmatization(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return ParallelWithProgress(n_jobs=config.n_parallel_jobs, progress_callback=None)(
            delayed(apply_lemmatization)(a) for a in X
        )

    def get_params(self, deep=False):
        return {}

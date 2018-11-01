#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from collections import OrderedDict

import numpy
from nltk import word_tokenize, sent_tokenize
from sklearn.base import TransformerMixin
from sklearn.externals.joblib import delayed, Parallel

from newsgac import config
from newsgac.data_engineering.preprocessing import remove_stop_words, apply_lemmatization

unwanted_chars = {
    u'|',
    u'_',
    u'=',
    u'(',
    u')',
    u'[',
    u']',
    u'<',
    u'>',
    u'#',
    u'/',
    u'\\',
    u'*',
    u'~',
    u'`',
    u'«',
    u'»',
    u'®',
    u'^',
    u'°',
    u'•',
    u'★',
    u'■',
    u'{',
    u'}',
    u'™',
    u'§',
    u'♦',
    u'±',
    u'►',
    u'и',
    u'✓',
    u'з',
    u'□',
    u'▼',
}


class CleanOCR(TransformerMixin):
    def fit(self, X, y=None):
        return self

    @staticmethod
    def transform_text(text):
        for char in unwanted_chars:
            text = text.replace(char, '')
        # TODO: find a better fix for this
        text = re.sub(u"(\u201e|\u201d|\u2014|\xeb|\xfc|\xe9|\xef|\xe8)", "", text)
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
            sentences = [s for s in sent_tokenize(text) if s]
            percentage = float(nr_subs) / len(sentences)
            list_nr_subs.append(numpy.array([nr_subs, percentage]))
        return numpy.array(list_nr_subs)

    def get_feature_names(self):
        return ['direct_quotes',
                'direct_quotes_perc']

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
        for char in [u'$', u'€', u'£', u'ƒ']:
            currency_symbols += text.count(char)
        features['currency_symbols_perc'] = currency_symbols / float(word_token_count) if word_token_count > 0 else 0
        features['digits_perc'] = len([c for c in text if c.isdigit()]) / float(word_token_count) if word_token_count > 0 else 0

        features['sentences'] = len(sentence_tokens)
        features['avg_sentence_length'] = (word_token_count / float(sentence_token_count)) if sentence_token_count > 0 else 0

        return numpy.array([value for idx, value in features.iteritems()])

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
        from pattern.nl import sentiment
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

class StopWordRemoval(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return Parallel(n_jobs=config.n_parallel_jobs)(
            delayed(remove_stop_words)(a) for a in X
        )

    def get_params(self, deep=False):
        return {}


class ApplyLemmatization(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return Parallel(n_jobs=config.n_parallel_jobs)(
            delayed(apply_lemmatization)(a) for a in X
        )

    def get_params(self, deep=False):
        return {}

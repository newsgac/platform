#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re


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
    # this function was duplicated two-three times, but sometimes with ws space:
    #clean_ocr, nr_subs = re.subn(pattern, ' ', ocr)
    clean_ocr = ' '.join(clean_ocr.split())

    return clean_ocr, nr_subs

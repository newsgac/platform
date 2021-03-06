import logging
import re

import dateparser

from newsgac.data_sources.models import Article, DataSource

logger = logging.getLogger(__name__)


class NewsgacFormatParser:
    @staticmethod
    def set_article_key_value(article, key, value):
        if key == 'DATE':
            date = dateparser.parse(value)
            article.date = date
            article.year = date.year
        elif key == 'NEWSPAPER':
            article.source = value
        elif key == 'PAGE':
            article.page = value
        elif key == 'URLS':
            article.urls = value.split(',')
        else:
            pass  # LENGTH or unknown key

    @staticmethod
    def parse_article(article_str):
        if isinstance(article_str, bytes):
            article_str = article_str.decode('utf-8')
        article = Article()
        # line = article_str.rstrip().decode('utf-8')
        line = article_str.rstrip()
        words = line.split(' ', 20)

        for word_index, word in enumerate(words):
            label_match = re.search('__label__(.*)', word)
            if label_match:
                article.label = label_match.groups(0)[0]
            else:
                key_value_match = re.search('^(\w*)?=(.*)$', word)
                if key_value_match:
                    NewsgacFormatParser.set_article_key_value(article, key_value_match.groups(0)[0], key_value_match.groups(0)[1])
                else:
                    break

        article.raw_text = ' '.join(words[word_index::])

        if article.label is None:
            raise ValueError('No label found in article string')
        if not article.raw_text:
            raise ValueError('No text found in article string')

        return article

    @staticmethod
    def get_articles_from_data_source(ds: DataSource):
        file = ds.file.file
        duplicate_count = 0
        articles = []

        for line_number, line in enumerate(file.read().splitlines()):
            try:
                article = NewsgacFormatParser.parse_article(line)
            except ValueError as e:
                raise Exception("Error in line %s: %s" % (str(line_number), e))

            articles.append(article)
            if article.raw_text in [a.raw_text for a in articles]:
                duplicate_count += 1

        logger.info(("Found ", duplicate_count, " duplicate(s) in documents.."))

        return articles
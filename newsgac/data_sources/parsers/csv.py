import logging
import pandas

from newsgac.data_sources.models import Article, DataSource

logger = logging.getLogger(__name__)


class CSVParser:
    @staticmethod
    def get_articles_from_data_source(ds: DataSource):
        df = pandas.read_csv(ds.file.file)
        assert ds.csv_label_field in df.columns
        assert ds.csv_text_field in df.columns
        articles = []
        for idx, row in df.iterrows():
            article = Article()
            article.raw_text = row[ds.csv_text_field]
            article.label = row[ds.csv_label_field]
            articles.append(article)

        return articles
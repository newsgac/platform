# coding=utf-8
from pymodm import MongoModel, EmbeddedDocumentField

from newsgac.data_sources.models import Article


class ArticleRef(MongoModel):
    article = EmbeddedDocumentField(Article)


def test_article_does_not_convert(app):
    raw_text = u'é'
    # character should be encoded as two unicode bytes
    assert raw_text.encode('utf-8') == '\xc3\xa9'

    article = Article(raw_text=raw_text)
    assert article.raw_text.encode('utf-8') == '\xc3\xa9'

    ref = ArticleRef(article=article)
    ref.save()

    ref = ArticleRef.objects.first()
    assert ref.article.raw_text.encode('utf-8') == '\xc3\xa9'

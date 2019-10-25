# coding=utf-8
from pymodm import MongoModel, EmbeddedDocumentField

from newsgac.data_sources.models import Article


class ArticleRef(MongoModel):
    article = EmbeddedDocumentField(Article)


def test_article_does_not_convert(app):
    raw_text = u'é'
    # character should be encoded as two unicode bytes
    if not raw_text.encode('utf-8') == '\xc3\xa9': raise AssertionError()

    article = Article(raw_text=raw_text)
    if not article.raw_text.encode('utf-8') == '\xc3\xa9': raise AssertionError()

    ref = ArticleRef(article=article)
    ref.save()

    ref = ArticleRef.objects.first()
    if not ref.article.raw_text.encode('utf-8') == '\xc3\xa9': raise AssertionError()

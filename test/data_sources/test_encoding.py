# coding=utf-8
from pymodm import MongoModel, EmbeddedDocumentField

from newsgac.data_sources.models import Article


class ArticleRef(MongoModel):
    article = EmbeddedDocumentField(Article)


def test_article_does_not_convert(app):
    raw_text = 'é'
    # character should be encoded as two unicode bytes
    if not raw_text == b'\xc3\xa9'.decode('utf-8'): raise AssertionError()

    article = Article(raw_text=raw_text)
    if not article.raw_text == b'\xc3\xa9'.decode('utf-8'): raise AssertionError()

    ref = ArticleRef(article=article)
    ref.save()

    ref = ArticleRef.objects.first()
    if not ref.article.raw_text == b'\xc3\xa9'.decode('utf-8'): raise AssertionError()

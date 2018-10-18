from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline as SKPipeline


def dict_vectorize(transformer_name, transformer):
    return SKPipeline([
        (transformer_name, transformer), ('DictVectorizer', DictVectorizer(sparse=False))
    ])

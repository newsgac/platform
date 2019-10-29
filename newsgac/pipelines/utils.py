from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline as SKPipeline
import numpy


def dict_vectorize(transformer_name, transformer):
    return SKPipeline([
        (transformer_name, transformer), ('DictVectorizer', DictVectorizer(sparse=False))
    ])

# Utility function to report best scores
def report(results, n_top=3):
    for i in range(1, n_top + 1):
        candidates = numpy.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print(("Model with rank: {0}".format(i)))
            print(("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  results['mean_test_score'][candidate],
                  results['std_test_score'][candidate])))
            print(("Parameters: {0}".format(results['params'][candidate])))
            print("")
import numpy
from pymodm.errors import DoesNotExist
from sklearn.externals.joblib import delayed
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold, cross_val_predict, cross_val_score
from sklearn.preprocessing import RobustScaler, MinMaxScaler

from learners import LearnerNB
from newsgac.caches.models import Cache
from newsgac.common.json_encoder import _dumps
from parallel_with_progress import ParallelWithProgress
import hashlib

from pipelines.data_engineering.postprocessing import Result
from pipelines.data_engineering.preprocessing import remove_stop_words, apply_lemmatization, get_clean_ocr

n_parallel_jobs = 8


def apply_function(function):
    def apply(article):
        article['text'] = function(article['text'])
    return apply

def remove_stop_words_in_article(article):
    article['text'] = remove_stop_words(article['text'])


def apply_lemmatization_in_article(article):
    article['text'] = apply_lemmatization(article['text'])


# def apply_nlp_in_article(nlp_tool, article):
#     article['features'] = nlp_tool.get_features(article['text'])


def apply_clean_ocr(article):
    article['text'] = get_clean_ocr(article['text'])


def get_pipeline_features_cache_hash(pipeline):
    pipeline_dict = pipeline.to_son().to_dict()
    pipeline_cache_repr = {
        'nlp_tool': pipeline_dict['nlp_tool'],
        'sw_removal': pipeline_dict['sw_removal'],
        'lemmatization': pipeline_dict['lemmatization']
    }
    return hashlib.sha1(_dumps(pipeline_cache_repr)).hexdigest()


def run_pipeline(pipeline):
    articles = [
        {
            'index': index,
            'text': article.raw_text,
            'label': article.label
        } for index, article in enumerate(pipeline.data_source.articles)]

    if len(articles) == 0:
        raise ValueError('No articles in data source')

    pipeline_features_cache_hash = get_pipeline_features_cache_hash(pipeline)

    try:
        pipeline.features = Cache.objects.get({'hash': pipeline_features_cache_hash})

    except DoesNotExist:
        # ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
        #     delayed(apply_clean_ocr)(a) for a in articles
        # )
        #
        if pipeline.sw_removal:
            ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
                delayed(remove_stop_words_in_article)(a) for a in articles
            )

        if pipeline.lemmatization:
            ParallelWithProgress(n_jobs=n_parallel_jobs, progress_callback=None)(
                delayed(apply_lemmatization_in_article)(a) for a in articles
            )

        # if pipeline.nlp_tool:
        #     ParallelWithProgress(n_jobs=1, progress_callback=None)(
        #         delayed(apply_nlp_in_article)(pipeline.nlp_tool, a) for a in articles
        #     )

        if pipeline.nlp_tool:
            feature_names, features = pipeline.nlp_tool.get_features(articles)
            pipeline.features = Cache(
                hash=pipeline_features_cache_hash,
                data={
                    'names': feature_names,
                    'values': features,
                }
            )
            pipeline.features.save()
            pipeline.save()

        features = pipeline.features.data['values']
        training_features = features[pipeline.data_source.train_indices]
        testing_features = features[pipeline.data_source.test_indices]

        if pipeline.nlp_tool.parameters.scaling:
            scaler = RobustScaler(copy=False).fit(training_features)
            scaler.transform(training_features)
            scaler.transform(testing_features)

        # todo: abstract this?
        if isinstance(pipeline.learner, LearnerNB):
            # NB Can't handle negative feature values
            scaler = MinMaxScaler(feature_range=(0, 1), copy=False).fit(training_features)
            scaler.transform(training_features)
            scaler.transform(testing_features)

        labels = numpy.array([article['label'] for article in articles])
        training_labels = labels[pipeline.data_source.train_indices]
        testing_labels = labels[pipeline.data_source.test_indices]

        pipeline.learner.fit(training_features, training_labels)
        pipeline.save()
        validation = validate(
            pipeline.learner.trained_model,
            training_features,
            training_labels,
            testing_features,
            testing_labels
         )
        print(validation)
        pass

def validate(trained_model, training_features, training_labels, testing_features, testing_labels):
        features = numpy.concatenate((training_features, testing_features))
        labels = numpy.concatenate((training_labels, testing_labels))

        cv = KFold(n_splits=10, random_state=42, shuffle=True)
        y_pred = cross_val_predict(estimator=trained_model, X=features, y=labels, method='predict', cv=cv)
        results_eval = Result(y_test=labels, y_pred=y_pred)

        print ("Number of eval samples")
        print len(features)
        scores = cross_val_score(trained_model, features, labels, cv=cv)
        print("Eval Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        results_eval.accuracy = format(scores.mean(), '.2f')
        results_eval.std = format(scores.std() * 2, '.2f')

        # trained_model results
        y_pred_mod = trained_model.predict(testing_features)
        results_model = Result(y_test=testing_labels, y_pred=y_pred_mod)

        print ("Number of test samples")
        print len(testing_features)
        # scores = cross_val_score(classifier, self.X_test, self.y_test, cv=cv)
        # print("Test CrossVal Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        acc = accuracy_score(y_true=testing_labels, y_pred=y_pred_mod)
        print("Model Accuracy: %0.4f" % acc)
        # results_model.accuracy = format(scores.mean(), '.2f')
        results_model.accuracy = format(acc, '.2f')

        return results_eval, results_model

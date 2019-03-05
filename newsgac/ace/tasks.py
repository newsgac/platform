import subprocess
import sys
from copy import deepcopy

import numpy as np
from bson import ObjectId
from anchor import anchor_text

from lime.lime_tabular import LimeTabularExplainer
from lime.lime_text import LimeTextExplainer
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline as SKPipeline

from newsgac.cached_views.models import CachedView
from newsgac.genres import genre_labels
from newsgac.pipelines import Pipeline
from newsgac.tasks.models import Status

from newsgac.ace.models import ACE, DUTCH_NLP
from newsgac.tasks.celery_app import celery_app


def get_predictions(articles, pipelines):
    # todo: parallelize
    # pipeline predictions are (hopefully) already parallelized for multiple articles at the same time
    # we could still paralellize multiple pipelines
    predictions = []
    for idx, pipeline in enumerate(pipelines):
        predictions.append(
            pipeline.sk_pipeline.get().predict([article.raw_text for article in articles]))
    # transpose so first axis is now article e.g. predictions[0][1] is article 0, pipeline 1
    return np.array(predictions).transpose()


def run_ace_impl(ace_id):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    ace.task.set_started()
    ace.save()
    try:
        ace.predictions = get_predictions(ace.data_source.articles, ace.pipelines)
        ace.task.set_success()
        ace.save()
    except Exception as e:
        t, v, tb = sys.exc_info()
        ace.task.status = Status.FAILURE
        ace.task.set_failure(e)
        ace.save()
        raise t, v, tb


@celery_app.task(bind=True, trail=True)
def run_ace(self, ace_id):
    # run_ace_impl(ace_id)
    process = subprocess.Popen(['python'], stdin=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate("""
import newsgac.database
from newsgac.ace.tasks import run_ace_impl
run_ace_impl('%s')
""" % ace_id)


    exit_code = process.wait()

    print(exit_code)
    print(stderrdata)
    print(stdoutdata)


def get_lime_text_explanation(raw_text, prediction, used_class_names, predict_proba):
    # note for bow=False: Only set to false if the classifier uses word order in some way (bigrams, etc).
    exp_lime = LimeTextExplainer(class_names=used_class_names, bow=True)
    return exp_lime.explain_instance(
        raw_text,
        predict_proba,
        labels=[prediction]
        # num_features=24,
        # num_samples=3000
    )


def get_lime_feature_explanation(article, prediction, skp, predict_proba, training_articles, used_class_names):
    feature_names = skp.named_steps['FeatureExtraction'].get_feature_names()

    # calculate feature vectors for explanators
    data = skp.transform([a.raw_text for a in training_articles])
    # labels = [a.label for a in training_articles]
    if isinstance(data, csr_matrix):
        data = data.toarray()

    exp_lime = LimeTabularExplainer(
        training_data=data,
        feature_names=feature_names,
        class_names=used_class_names
    )
    # exp_anchor = anchor_tabular.AnchorTabularExplainer(data=data, feature_names=feature_names,
    #                                                        class_names=used_class_names, categorical_names=[])
    # TODO: check with hold-out-dataset
    # anchor needs validation data
    # X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.5, random_state=42)
    # exp_anchor.fit(train_data=X_train, train_labels=y_train, validation_data=X_test,
    #                    validation_labels=y_test)

    feature_list = skp.transform([article.raw_text])
    if isinstance(feature_list, csr_matrix):
        feature_list = feature_list.toarray()
    article_features = feature_list[0]

    # TODO: check the order of features with feature_names
    return exp_lime.explain_instance(
        article_features,
        predict_proba,
        labels=[prediction],
        # num_features=24,
        # num_samples=3000
    )


def get_anchor_text_explanation(skp, raw_text, predict, used_class_names):
    exp_anchor = anchor_text.AnchorText(DUTCH_NLP, class_names=used_class_names,
                                        use_unk_distribution=False)

    # need to send clean ocr to anchor
    # TODO: applying a dirty fix right now, we need to look into encoding/decoding changes made in transformers.py
    # clean_text = skp.steps[0][1].transform([raw_text])[0]
    # TODO: Question: why aren't we removing quotes? It's contradicting with the feature descriptions
    # clean_text = RemoveQuotes().transform([clean_text])[0]

    clean_text = raw_text.encode('ascii', 'replace')

    return exp_anchor.explain_instance(clean_text, predict, use_proba=True)

def explain_article_lime_task_impl(view_cache_id, ace_id, pipeline_id, article_number):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})

    article_number = int(article_number)
    article = ace.data_source.articles[article_number]

    sk_pipeline = pipeline.sk_pipeline.get()

    prediction = sk_pipeline.predict([article.raw_text])[0]

    # do not modify pipeline.sk_pipeline
    skp = deepcopy(sk_pipeline)
    model = skp.steps.pop()[1]

    used_classes = model.classes_
    used_class_names = [genre_labels[x] for x in used_classes]

    lime_text_html = ''
    lime_features_html = ''
    anchor_html = ''

    # TODO: do not send article raw text, I suspect the bug report for stop-word appearance is due to raw_text
    # although we are sending through the pipeline predict_proba
    if pipeline.nlp_tool.name == 'TF-IDF':
        # the pipeline should be linear, but it contains a FeatureUnion (with a Pipeline), so let's flatten it
        steps = []  # will contained the flattened steps
        for step in sk_pipeline.steps:
            if isinstance(step[1], FeatureUnion):
                # step[1] FeatureUnion, should contain a single Pipeline
                steps.extend(step[1].transformer_list[0][1].steps)
            else:
                steps.append(step)

        # find tfidf vectorizer step number
        for tfidf_step_index, step in enumerate(steps):
            if isinstance(step[1], TfidfVectorizer):
                break

        preprocess_pipeline = SKPipeline(steps[:tfidf_step_index])
        rest_pipeline = SKPipeline(steps[tfidf_step_index:])

        # give lime text before tfidf_step, the function should be the rest of the pipeline.
        print article.raw_text
        lime_text_html = get_lime_text_explanation(
            preprocess_pipeline.transform([article.raw_text])[0],
            prediction,
            used_class_names,
            rest_pipeline.predict_proba
        ).as_html()

        # anchor_html = get_anchor_text_explanation(
        #     skp,
        #     article.raw_text,
        #     sk_pipeline.predict,
        #     used_class_names
        # ).as_html()

    else:
        lime_features_html = get_lime_feature_explanation(
            article,
            prediction,
            skp,
            model.predict_proba,
            pipeline.data_source.articles,
            used_class_names
        ).as_html()

    cache = CachedView.objects.get({'_id': ObjectId(view_cache_id)})
    cache.task.set_success()
    cache.data = dict(
        pipeline=pipeline,
        article=article,
        prediction=prediction,
        exp1_html=lime_text_html or lime_features_html,
        exp2_html=anchor_html,
        article_number=article_number,
    )
    cache.save()


@celery_app.task(bind=True)
def explain_article_lime_task(self, view_cache_id, ace_id, pipeline_id, article_number):
    # explain_article_lime_task_impl(view_cache_id, ace_id, pipeline_id, article_number)
    # return
    process = subprocess.Popen(['python'], stdin=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate("""
import newsgac.database
from newsgac.ace.tasks import explain_article_lime_task_impl
explain_article_lime_task_impl('%s', '%s', '%s', '%s')
    """ % (view_cache_id, ace_id, pipeline_id, article_number))

    exit_code = process.wait()
    if exit_code > 0:
        raise Exception("Subprocess exited with exit_code " + str(exit_code))

    print(exit_code)
    print(stderrdata)
    print(stdoutdata)




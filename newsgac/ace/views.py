from __future__ import absolute_import
from bson import ObjectId
from bokeh.embed import components
from bokeh.layouts import gridplot
from flask import Blueprint, render_template, request, url_for, redirect, session, json

from newsgac.ace.models import ACE, DUTCH_NLP
from newsgac.common.back import back
from newsgac.common.utils import model_to_json, model_to_dict
from newsgac.data_engineering.utils import LABEL_DICT
from newsgac.pipelines.models import Pipeline
from newsgac.data_sources.models import DataSource
from newsgac.users.models import User
from newsgac.users.view_decorators import requires_login
from newsgac.visualisation.comparison import PipelineComparator
from newsgac.visualisation.resultvisualiser import ResultVisualiser
from newsgac.ace.tasks import run_ace

from anchor import anchor_tabular
from anchor import anchor_text
from lime.lime_tabular import LimeTabularExplainer
from lime.lime_text import LimeTextExplainer
from sklearn.model_selection import train_test_split
from sklearn import preprocessing

from copy import deepcopy
import numpy as np
from newsgac.nlp_tools.transformers import ExtractQuotes, RemoveQuotes

ace_blueprint = Blueprint('ace', __name__)


@ace_blueprint.route('/')
@requires_login
@back.anchor
def overview():
    aces = [
        {
            'id': str(ace._id),
            'created': ace.created,
            'display_title': ace.display_title,
            'data_source': {
                'display_title': ace.data_source.display_title
            },
            'task': json.dumps(ace.task.as_dict()),

        } for ace in list(ACE.objects.all())
    ]

    # data_sources = list(DataSource.objects.all())
    data_sources = list(DataSource.objects.raw({'training_purpose': False}))
    pipelines = list(Pipeline.objects.all())
    return render_template(
        "ace/overview.html",
        aces=aces,
        pipelines=pipelines,
        data_sources=data_sources,
    )


@ace_blueprint.route('/new', methods=['GET'])
@requires_login
@back.anchor
def new():
    data_sources = list(DataSource.objects.all())
    pipelines = list(Pipeline.objects.all())
    return render_template(
        "ace/overview.html",
        pipelines=pipelines,
        data_sources=data_sources,
    )


@ace_blueprint.route('/new', methods=['POST'])
@requires_login
def new_save():
    ace = ACE()
    ace.data_source = DataSource.objects.get({'_id': ObjectId(request.form['data_source'])})
    ace.pipelines = [Pipeline.objects.get({'_id': ObjectId(pipeline_id)}) for pipeline_id in request.form.getlist('pipelines[]')]
    ace.user = User(email=session['email'])
    ace.display_title = ace.data_source.display_title + ' (' + ', '.join(p.display_title for p in ace.pipelines) + ')'
    ace.save()
    task = run_ace.delay(str(ace._id))
    ace.task_id = task.task_id
    ace.save()
    return redirect(url_for('ace.overview'))


@ace_blueprint.route('/<string:ace_id>')
@requires_login
def view(ace_id):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})

    pipelines = [model_to_dict(pipeline) for pipeline in ace.pipelines]
    articles = [{
        'raw_text': article.raw_text.encode('utf-8'),
        # 'predictions': [p.encode('utf-8') for p in ace.predictions[idx]],
        'predictions': [LABEL_DICT[p].encode('utf-8') for p in ace.predictions[idx]],
        'label': article.label.encode('utf-8'),
    } for idx, article in enumerate(ace.data_source.articles)]

    return render_template(
        "ace/run.html",
        # ace=ace,
        # genre_codes=genre_codes,
        # genre_labels=genre_labels,
        ace_id=ace_id,
        pipelines=pipelines,
        articles=articles
    )


@ace_blueprint.route('/<string:ace_id>/delete')
@requires_login
def delete(ace_id):
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    ace.delete()

    return back.redirect()


@ace_blueprint.route('/delete_all')
@requires_login
def delete_all():
    for ace in list(ACE.objects.all()):
        ace.delete()

    return back.redirect()


# article number is an integer, but you should leave string here so that we can
# generate a url template that can be used dynamically from Javascript
@ace_blueprint.route('/<string:ace_id>/explain_features_lime/<string:pipeline_id>/<string:article_number>')
@requires_login
def explain_article(ace_id, pipeline_id, article_number):
    html_lime = None
    html_anchor = "\n"
    ace = ACE.objects.get({'_id': ObjectId(ace_id)})
    pipeline = Pipeline.objects.get({'_id': ObjectId(pipeline_id)})

    article_number = int(article_number)
    article = ace.data_source.articles[article_number]

    prediction = pipeline.sk_pipeline.predict([article.raw_text])[0]

    # do not modify pipeline.sk_pipeline
    skp = deepcopy(pipeline.sk_pipeline)
    model = skp.steps.pop()[1]

    used_classes = np.array(model.classes_).tolist()
    used_class_names = np.array([LABEL_DICT[clss] for clss in used_classes]).tolist()

    class_idx = []
    for i, clss in enumerate(used_class_names):
        class_idx.append(i)

    if pipeline.nlp_tool.name == 'TF-IDF':
        exp_lime = LimeTextExplainer(class_names=used_class_names)
        exp_anchor = anchor_text.AnchorText(DUTCH_NLP, class_names=used_class_names,
                                                 use_unk_distribution=False)

        exp_from_lime = exp_lime.explain_instance(
            article.raw_text,
            pipeline.sk_pipeline.predict_proba,
            labels=class_idx,
            # num_features=24,
            # num_samples=3000
        )

        # need to send clean ocr to anchor
        # TODO: applying a dirty fix right now, we need to look into encoding/decoding changes made in transformers.py
        clean_text = skp.steps[0][1].transform([article.raw_text])[0]
        # TODO: Question: why aren't we removing quotes? It's contradicting with the feature descriptions
        # clean_text = RemoveQuotes().transform([clean_text])[0]

        exp_from_anchor = exp_anchor.explain_instance(clean_text, pipeline.sk_pipeline.predict, use_proba=True)

        html_anchor = exp_from_anchor.as_html()

    else:
        feature_extractor = skp
        feature_names = skp.named_steps['FeatureExtraction'].get_feature_names()

        # calculate feature vectors for explanators
        data = feature_extractor.transform([a.raw_text for a in pipeline.data_source.articles])
        labels = [a.label for a in pipeline.data_source.articles]
        exp_lime = LimeTabularExplainer(training_data=data, feature_names=feature_names,
                                            class_names=used_class_names)
        # exp_anchor = anchor_tabular.AnchorTabularExplainer(data=data, feature_names=feature_names,
        #                                                        class_names=used_class_names, categorical_names=[])
        # TODO: check with hold-out-dataset
        # anchor needs validation data
        # X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.5, random_state=42)
        # exp_anchor.fit(train_data=X_train, train_labels=y_train, validation_data=X_test,
        #                    validation_labels=y_test)

        article_features = feature_extractor.transform([article.raw_text])[0]

        # TODO: check the order of features with feature_names
        exp_from_lime = exp_lime.explain_instance(
            article_features,
            model.predict_proba,
            labels=class_idx,
            #num_features=24,
            # num_samples=3000
        )

        # exp_from_anchor = exp_anchor.explain_instance(article_features, model.predict_proba)

    html_lime = exp_from_lime.as_html(labels=[prediction])

    return render_template(
        'pipelines/explain.html',
        pipeline=pipeline,
        article=article,
        prediction=LABEL_DICT[prediction],
        exp1_html=html_lime,
        exp2_html=html_anchor,
        article_number=article_number,
    )

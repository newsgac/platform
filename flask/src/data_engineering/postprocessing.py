from __future__ import division

import numpy as np
import dill
from src.run import DATABASE
from sklearn.metrics import confusion_matrix
import src.data_engineering.utils as DataUtils
from src.models.data_sources.data_source import DataSource
import src.models.data_sources.constants as DataSourceConstants
from sklearn import metrics
from lime.lime_text import LimeTextExplainer
from lime.lime_tabular import LimeTabularExplainer
from sklearn.pipeline import make_pipeline
import src.data_engineering.feature_extraction as FE
from src.data_engineering.preprocessing import Preprocessor, process_raw_text_for_config

# np.random.seed(42)

__author__ = 'abilgin'

class Result(object):

    def __init__(self, y_test, y_pred):

        self.y_test = y_test
        self.y_pred = y_pred

        self.genre_names = []
        genre_order = []
        for number, name in DataUtils.genres.items():
            if 'Unlabelled' not in name:
                self.genre_names.append(''.join(name).split('/')[0])
                genre_order.append(number)


        #TODO: DEBUG here to see whether genre names and confusion matrix match
        self.confusion_matrix = confusion_matrix(self.y_test, self.y_pred, labels=sorted(genre_order))
        print self.confusion_matrix

        self.precision_weighted = format(metrics.precision_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.precision_micro = format(metrics.precision_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.precision_macro = format(metrics.precision_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.recall_weighted =format(metrics.recall_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.recall_micro =format(metrics.recall_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.recall_macro =format(metrics.recall_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.fmeasure_weighted = format(metrics.f1_score(self.y_test, self.y_pred, average='weighted'), '.2f')
        self.fmeasure_micro = format(metrics.f1_score(self.y_test, self.y_pred, average='micro'), '.2f')
        self.fmeasure_macro = format(metrics.f1_score(self.y_test, self.y_pred, average='macro'), '.2f')

        self.cohens_kappa = format(metrics.cohen_kappa_score(self.y_test, self.y_pred), '.2f')

        self.accuracy = 0

        np.set_printoptions(precision=2)

    def get_confusion_matrix(self):
        return self.confusion_matrix

    @staticmethod
    def normalise_confusion_matrix(cm):
        sum = cm.sum(axis=1)[:, np.newaxis]
        temp = cm.astype('float')
        # return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        return np.divide(temp, sum, out=np.zeros_like(temp), where=sum!=0)


class Explanation():

    def __init__(self, experiment, article, predicted_genre):
        self.experiment = experiment
        self.article = article
        self.predicted_genre = predicted_genre

    def explain_using_text(self):
        class_names =  [l[0] for l in sorted(DataUtils.genres_labels.items(), key=lambda x: x[1]) if l[0]!='Unlabelled']
        print class_names
        ds = DataSource.get_by_id(self.experiment.data_source_id)
        explainer = LimeTextExplainer(class_names=class_names)

        text_instance = self.article['article_raw_text']

        if 'nltk' not in ds.pre_processing_config.values():
            preprocessor = Preprocessor(config=ds.pre_processing_config)
            c = make_pipeline(FE.ArticleTransformer(text=text_instance, preprocessor=preprocessor), self.experiment.get_classifier())
        else:
            vectorizer = dill.loads(DATABASE.getGridFS().get(ds.vectorizer_handler).read())
            c = make_pipeline(vectorizer, self.experiment.get_classifier())

        lbls = [(DataUtils.genres_labels[k] - 1) for k in class_names]
        print lbls
        exp = explainer.explain_instance(text_instance=text_instance, classifier_fn=c.predict_proba,
                                         num_features=10, labels=lbls, num_samples=5000)
        print('Article: %s' % self.article['article_raw_text'] )
        print "Predictions: ", self.experiment.predict(text_instance, ds)
        print('Predicted class from GUI =', self.predicted_genre)

        for k in class_names:
            print ('Explanation for class %s' % k)
            print ('\n'.join(map(str, exp.as_list(label=DataUtils.genres_labels[k]-1))))

        return exp.as_html(labels=lbls)


    def explain_using_features(self):
        class_names = [l[0] for l in sorted(DataUtils.genres_labels.items(), key=lambda x: x[1]) if
                       l[0] != 'Unlabelled']
        print class_names
        ds = DataSource.get_by_id(self.experiment.data_source_id)
        training_data = np.array(dill.loads(DATABASE.getGridFS().get(ds.X_train_handler).read()))
        sorted_keys = sorted(self.experiment.features.keys())
        print sorted_keys
        f_names = [f for f in sorted_keys if f not in DataSourceConstants.NON_FEATURE_COLUMNS]
        explainer = LimeTabularExplainer(training_data=training_data, feature_names=f_names,class_names=class_names)

        preprocessor = Preprocessor(config=ds.pre_processing_config)
        processed_text, features, id = process_raw_text_for_config(preprocessor, self.article['article_raw_text'])
        # c = make_pipeline(ArticleTransformer(text=self.article['article_raw_text'], preprocessor=preprocessor),
        #                   self.experiment.get_classifier())


        lbls = [(DataUtils.genres_labels[k] - 1) for k in class_names]
        print lbls
        print np.array(features.values())

        # print DataUtils.genres_labels
        # exp = explainer.explain_instance(text_instance=text_instance, classifier_fn=c.predict_proba,
        #                                  num_features=5, labels=[DataUtils.genres_labels[self.predicted_genre]])
        exp = explainer.explain_instance(data_row=np.array(features.values()), predict_fn=self.experiment.get_classifier().predict_proba,
                                         num_features=10, labels=lbls, num_samples=5000)

        print('Article: %s' % self.article['article_raw_text'])
        print "Predictions: ", self.experiment.predict(self.article['article_raw_text'], ds)
        print('Predicted class from GUI =', self.predicted_genre)

        for k in class_names:
            print ('Explanation for class %s' % k)
            print ('\n'.join(map(str, exp.as_list(label=DataUtils.genres_labels[k] - 1))))
            # fig = exp.as_pyplot_figure(label=(val-1))
            # import matplotlib.pyplot as plt
            # plt.show(fig)

        return exp.as_html(labels=lbls)

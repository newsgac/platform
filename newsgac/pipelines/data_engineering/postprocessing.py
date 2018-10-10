from __future__ import division

import numpy as np
from newsgac.database import DATABASE
import pipelines.data_engineering.utils as DataUtils
# from newsgac.models.data_sources.data_source_old import DataSource
# import newsgac.models.data_sources.constants as DataSourceConstants
from lime.lime_text import LimeTextExplainer
from lime.lime_tabular import LimeTabularExplainer
from sklearn.pipeline import make_pipeline
from pipelines.data_engineering.preprocessing import Preprocessor, process_raw_text_for_config, get_clean_ocr, remove_stop_words, apply_lemmatization

# np.random.seed(42)

__author__ = 'abilgin'


class Explanation():

    def __init__(self, experiment, article, predicted_genre):
        self.experiment = experiment
        self.article = article
        self.predicted_genre = predicted_genre

    def explain_using_text(self):
        class_names =  [l[0] for l in sorted(DataUtils.genres_labels.items(), key=lambda x: x[1]) if l[0]!='Unlabelled']
        ds = DataSource.get_by_id(self.experiment.data_source_id)
        explainer = LimeTextExplainer(class_names=class_names)

        text_instance = self.article['article_raw_text'].lower()
        clean_ocr = get_clean_ocr(text_instance)

        if 'sw_removal' in ds.pre_processing_config.keys():
            clean_ocr = remove_stop_words(clean_ocr)
        if 'lemmatization' in ds.pre_processing_config.keys():
            clean_ocr = apply_lemmatization(clean_ocr)

        # if 'tf-idf' not in ds.pre_processing_config.values():
        #     preprocessor = Preprocessor(config=ds.pre_processing_config)
        #     c = make_pipeline(FE.ArticleTransformer(text=text_instance, preprocessor=preprocessor), self.experiment.get_classifier())
        # else:
        vectorizer = DATABASE.load_object(ds.vectorizer_handler)
        c = make_pipeline(vectorizer, self.experiment.get_classifier())

        lbls = [(DataUtils.genres_labels[k] - 1) for k in class_names]

        exp = explainer.explain_instance(text_instance=clean_ocr, classifier_fn=c.predict_proba,
                                         num_features=8, labels=lbls, num_samples=7000)
        # exp = explainer.explain_instance(text_instance=clean_ocr, classifier_fn=c.predict_proba,
        #                                  num_features=6, labels=(DataUtils.genres_labels[self.predicted_genre]-1,), num_samples=7000)
        print('Article: %s' % self.article['article_raw_text'] )
        print "Predictions: ", self.experiment.predict(text_instance, ds)
        print('Predicted class from GUI =', self.predicted_genre)

        for k in class_names:
            print ('Explanation for class %s' % k)
            print ('\n'.join(map(str, exp.as_list(label=DataUtils.genres_labels[k]-1))))

        # return exp.as_html(labels=lbls)
        return exp.as_html(labels=(DataUtils.genres_labels[self.predicted_genre]-1,))


    def explain_using_features(self):
        class_names = [l[0] for l in sorted(DataUtils.genres_labels.items(), key=lambda x: x[1]) if
                       l[0] != 'Unlabelled']
        ds = DataSource.get_by_id(self.experiment.data_source_id)
        training_data = np.array(DATABASE.load_object(ds.X_train_handler))

        if 'scaling' in ds.pre_processing_config.keys():
            # revert the data back to original
            scaler = DATABASE.load_object(ds.scaler_handler)
            training_data = scaler.inverse_transform(training_data)
            c = make_pipeline(scaler, self.experiment.get_classifier())
        else:
            c = make_pipeline(self.experiment.get_classifier())

        sorted_keys = sorted(self.experiment.features.keys())
        f_names = [f for f in sorted_keys if f not in DataSourceConstants.NON_FEATURE_COLUMNS]
        explainer = LimeTabularExplainer(training_data=training_data, feature_names=f_names, class_names=class_names)

        preprocessor = Preprocessor(config=ds.pre_processing_config)
        processed_text, features, id = process_raw_text_for_config(preprocessor, self.article['article_raw_text'])
        ordered_feature_values = [features[f] for f in sorted_keys if
                                  f not in DataSourceConstants.NON_FEATURE_COLUMNS]
        lbls = [(DataUtils.genres_labels[k] - 1) for k in class_names]

        exp = explainer.explain_instance(data_row=np.array(ordered_feature_values), predict_fn=c.predict_proba,
                                         num_features=8, labels=lbls, num_samples=7000)

        print('Article: %s' % self.article['article_raw_text'])
        print "Predictions: ", self.experiment.predict(self.article['article_raw_text'], ds)
        print('Predicted class from GUI =', self.predicted_genre)

        for k in class_names:
            print ('Explanation for class %s' % k)
            print ('\n'.join(map(str, exp.as_list(label=DataUtils.genres_labels[k] - 1))))

        # return exp.as_html(labels=lbls)
        return exp.as_html(labels=(DataUtils.genres_labels[self.predicted_genre] - 1,))
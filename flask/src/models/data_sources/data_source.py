import uuid
import datetime
from StringIO import StringIO

from sklearn.model_selection import train_test_split
import src.models.data_sources.constants as DataSourceConstants
import src.models.data_sources.errors as DataSourceErrors
from src.data_engineering.preprocessing import Preprocessor, remove_stop_words, apply_lemmatization, get_clean_ocr
from sklearn.feature_extraction.text import TfidfVectorizer
import dill
import numpy as np
from src.run import DATABASE
import src.common.utils as Utilities
import re
from bson import ObjectId
import src.data_engineering.utils as DataUtils

UT = Utilities.Utils()
ALLOWED_EXTENSIONS = {'txt', 'csv'}

__author__ = 'abilgin'

class DataSource(object):

    def __init__(self, user_email, display_title, description, training_purpose, secure_filename, **kwargs):

        if 'new_handler' in kwargs:
            # creation from the web
            self.user_email = user_email
            self._id = uuid.uuid4().hex
            self.created = datetime.datetime.utcnow()
            self.processing_started = None
            self.processing_completed = None
            self.file_handler_db = kwargs['new_handler']
            self.X_train_handler, self.X_test_handler, self.y_train_with_ids_handler, self.y_test_with_ids_handler = None, None, None, None
            self.pre_processing_config = None
        else:
            # default constructor from the database
            self.__dict__.update(kwargs)

        self.user_email = user_email
        self.display_title = display_title
        self.description = description
        self.secure_filename = secure_filename
        self.training_purpose = training_purpose

    @classmethod
    def get_by_id(cls, id):
        return cls(**DATABASE.find_one(DataSourceConstants.COLLECTION, {"_id": id}))

    @classmethod
    def get_by_user_email(cls, user_email):
        return [cls(**elem) for elem in DATABASE.find(DataSourceConstants.COLLECTION, {"user_email": user_email})]

    @classmethod
    def get_training_by_user_email(cls, user_email):
        return [cls(**elem) for elem in
                DATABASE.find(DataSourceConstants.COLLECTION, {"user_email": user_email, "training_purpose": True})]

    @classmethod
    def get_testing_by_user_email(cls, user_email):
        return [cls(**elem) for elem in
                DATABASE.find(DataSourceConstants.COLLECTION, {"user_email": user_email, "training_purpose": False})]

    @classmethod
    def get_processed_datasets(cls):
        return [cls(**elem) for elem in DATABASE.find(DataSourceConstants.COLLECTION, {"processing_completed": {"$ne": None}})]

    @classmethod
    def get_processed_by_user_email(cls, user_email):
        return [cls(**elem) for elem in
                DATABASE.find(DataSourceConstants.COLLECTION, {"user_email": user_email, "processing_completed": {"$ne": None}})]

    @classmethod
    def get_by_user_email_and_display_title(cls, user_email, display_title):
        return cls(**DATABASE.find_one(DataSourceConstants.COLLECTION, {"user_email": user_email,
                                                                        "display_title": display_title}))

    @staticmethod
    def get_training_titles_by_user_email(user_email, processed=False):
        ds_list = DataSource.get_training_by_user_email(user_email=user_email)
        titles = []
        for ds in ds_list:
            if processed and ds.processing_started is not None and ds.processing_completed is not None:
                titles.append(ds.display_title)
            elif not processed:
                titles.append(ds.display_title)

        return titles

    @staticmethod
    def is_source_unique(user_email, display_title):
        user_data_list = DataSource.get_by_user_email(user_email)

        for ds in user_data_list:
            if ds.user_email == user_email and ds.display_title == display_title:
                raise DataSourceErrors.ResourceDisplayTitleAlreadyExistsError("The display title is already taken.")

        return True

    def is_preprocessing_config_unique(self, new_config):
        user_data_list = DataSource.get_training_by_user_email(self.user_email)

        for ds in user_data_list:
            if ds.pre_processing_config == new_config and ds.secure_filename == self.secure_filename:
                raise DataSourceErrors.ProcessingConfigAlreadyExists("The pre_processing configuration already exists for this data (using the same filename).")
        return True

    def save_to_db(self):
        DATABASE.update(DataSourceConstants.COLLECTION, {"_id": self._id}, self.__dict__)

    def process_data_source(self, config):
        self.processing_started = datetime.datetime.utcnow()
        self.pre_processing_config = config
        self.save_to_db()

        # read and upload the raw data
        self.read_and_upload_dataset()

        articles_from_db = DataSource.get_articles_by_data_source(self._id)
        print "Read ", len(articles_from_db), " documents from db"


        if self.pre_processing_config == None:
            self.display_title = self.display_title + " (REAL)"

            X, y = self.get_data_with_labels_from_articles(articles_from_db)

            processed_X = []
            X_train = []
            for x in X:
                ocr = x['article_raw_text'].lower()
                processed_X.append(get_clean_ocr(ocr))
                X_train.append(x['article_raw_text'])

            X_test, y_train_with_ids, y_test_with_ids = processed_X, [], []
        else:

            if 'nltk' in self.pre_processing_config.values():
                self.display_title = self.display_title + " (NLTK)"
                if 'sw_removal' in self.pre_processing_config.keys():
                    self.display_title = self.display_title + " (SWR)"
                if 'lemmatization' in self.pre_processing_config.keys():
                    self.display_title = self.display_title + " (LEM)"

                X, y = self.get_data_with_labels_from_articles(articles_from_db)

                processed_X = []
                for x in X:
                    ocr = x['article_raw_text'].lower()
                    clean_ocr = get_clean_ocr(ocr)

                    if 'sw_removal' in self.pre_processing_config.keys():
                        clean_ocr = remove_stop_words(clean_ocr)
                    if 'lemmatization' in self.pre_processing_config.keys():
                        clean_ocr = apply_lemmatization(clean_ocr)

                    processed_X.append(clean_ocr)

                X_train, X_test, y_train_with_ids, y_test_with_ids = train_test_split(processed_X, y, random_state=42,
                                                                                      test_size=0.1, shuffle=False)

                # fit the vectorizer
                vectorizer = TfidfVectorizer(lowercase=False)
                train_vectors = vectorizer.fit_transform(X_train)
                self.vectorizer_handler = DATABASE.getGridFS().put(dill.dumps(vectorizer))
                self.train_vectors_handler = DATABASE.getGridFS().put(dill.dumps(train_vectors))
            else:
                if 'nlp_tool' in self.pre_processing_config.keys():
                    if self.pre_processing_config['nlp_tool'] == 'frog':
                        self.display_title = self.display_title + " (FROG)"
                    elif self.pre_processing_config['nlp_tool'] == 'spacy':
                        self.display_title = self.display_title + " (SPACY)"

                if 'sw_removal' in self.pre_processing_config.keys():
                    self.display_title = self.display_title + " (SWR)"
                if 'lemmatization' in self.pre_processing_config.keys():
                    self.display_title = self.display_title + " (LEM)"
                if 'scaling' in self.pre_processing_config.keys():
                    self.display_title = self.display_title + " (SCL)"

                self.apply_preprocessing_and_update_db(articles_from_db)

                X, y = self.get_data_with_labels_from_articles(DataSource.get_articles_by_data_source(self._id))

                X_train, X_test, y_train_with_ids, y_test_with_ids = train_test_split(X, y, random_state=42,
                                                                                      test_size=0.1, shuffle=False)

                if 'scaling' in self.pre_processing_config.keys():
                    print ("Scaling the data..")
                    from sklearn.preprocessing import MinMaxScaler
                    scaler = MinMaxScaler(feature_range=(-1, 1)).fit(X_train)
                    X_train = scaler.transform(X_train)
                    X_test = scaler.transform(X_test)
                    self.scaler_handler = DATABASE.getGridFS().put(dill.dumps(scaler))

        self.X_train_handler = DATABASE.getGridFS().put(dill.dumps(X_train))
        self.X_test_handler = DATABASE.getGridFS().put(dill.dumps(X_test))
        self.y_train_with_ids_handler = DATABASE.getGridFS().put(dill.dumps(y_train_with_ids))
        self.y_test_with_ids_handler = DATABASE.getGridFS().put(dill.dumps(y_test_with_ids))
        self.processing_completed = datetime.datetime.utcnow()
        self.save_to_db()

    def delete(self):
        DATABASE.remove(DataSourceConstants.COLLECTION, {"_id": self._id})
        DATABASE.remove(DataSourceConstants.COLLECTION_PROCESSED, {"data_source_id": self._id})
        DATABASE.getGridFS().delete(self.file_handler_db)
        DATABASE.getGridFS().delete(self.X_train_handler)
        DATABASE.getGridFS().delete(self.X_test_handler)
        DATABASE.getGridFS().delete(self.y_train_with_ids_handler)
        DATABASE.getGridFS().delete(self.y_test_with_ids_handler)

        if self.pre_processing_config != None:
            if 'nltk' in self.pre_processing_config.values():
                DATABASE.getGridFS().delete(self.vectorizer_handler)
                DATABASE.getGridFS().delete(self.train_vectors_handler)
            if 'scaling' in self.pre_processing_config.keys():
                DATABASE.getGridFS().delete(self.scaler_handler)

    def get_user_friendly_created(self):
        return UT.get_local_display_time(self.created)

    def get_user_friendly_processing_started(self):
        return UT.get_local_display_time(self.processing_started)

    def get_user_friendly_processing_finished(self):
        return UT.get_local_display_time(self.processing_completed)

    def get_processing_duration(self):
        delta = self.processing_completed - self.processing_started
        m, s = divmod(delta.seconds, 60)
        h, m = divmod(m, 60)
        if int(h) == 0:
            return "{:2d} minutes {:2d} seconds".format(int(m), int(s))

        return "{:2d} hours {:2d} minutes {:2d} seconds".format(int(h), int(m), int(s))

    @staticmethod
    def get_processed_article_by_id(id):
        return DATABASE.find_one(DataSourceConstants.COLLECTION_PROCESSED, {"_id": ObjectId(id)})

    @staticmethod
    def get_processed_article_by_raw_text(raw_text):
        return DATABASE.find_one(DataSourceConstants.COLLECTION_PROCESSED, {"article_raw_text": raw_text})

    @staticmethod
    def is_allowed(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def save_raw_to_db(self, dict):
        DATABASE.insert(DataSourceConstants.COLLECTION_PROCESSED, dict)

    def get_unprocessed_amount(self):
        return len([elem for elem in DATABASE.find(DataSourceConstants.COLLECTION_PROCESSED,
                                                   {'data_source_id': self._id,"features": { '$exists': False}})])

    def does_raw_text_exist(self, text):
        if DATABASE.find_one(DataSourceConstants.COLLECTION_PROCESSED, {'data_source_id': self._id, 'article_raw_text': text}):
            return True
        return False

    @staticmethod
    def get_articles_by_data_source(data_source_id):
        # BUG FIX: retrieve the documents having all the features, checking with one is sufficient
        return [elem for elem in DATABASE.find(DataSourceConstants.COLLECTION_PROCESSED,
                                               {"data_source_id": data_source_id})]

    def add_features_to_db(self, article_id, dict):
        DATABASE.update(DataSourceConstants.COLLECTION_PROCESSED, {'_id': article_id, 'data_source_id': self._id}, {'$set': dict})

    def is_article_processed(self, article_id):
        doc = DATABASE.find_one(DataSourceConstants.COLLECTION_PROCESSED, {'_id': article_id})
        if set(doc.keys()) == set(DataUtils.feature_descriptions.keys()):
            return True

        return False

    def read_and_upload_dataset(self):

        file = DATABASE.getGridFS().get(self.file_handler_db).read()
        label_list = []
        raw_text_list = []
        date_list = []
        count = 0
        no_date = False
        for line in file.splitlines():
            line = line.rstrip()

            # groups = re.search(r'^__label__(.{3}.+)DATE\=([\0-9]+) ((?s).*)$', line).groups()
            # groups = re.search(r'^__label__(.{3}.+)DATE\=([\0-9]+[^&]) ((?s).*)$', line).groups()
            reg_res = re.search(r'^__label__(.{3}.+)DATE\=(\d{1,}\/\d{1,}\/\d{2,}) ((?s).*)$', line)

            if not reg_res:
                # no date
                reg_res = re.search(r'^__label__(.{3})((?s).*)', line)
                no_date = True

            groups = reg_res.groups()
            label = groups[0].rstrip()
            if no_date:
                date = None
                raw_text = groups[1].rstrip()
            else:
                date_str = groups[1].rstrip()
                month = date_str.split("/")[0]
                day = date_str.split("/")[1]
                year = date_str.split("/")[2]

                if len(year) == 2:
                    # fix for conversion 20xx where xx < 69 although the data is from 1900s
                    date_str_corr = day + "/" + month + "/19" + year
                else:
                    date_str_corr = day + "/" + month + "/" + year
                # print date_str_corr
                date = datetime.datetime.strptime(date_str_corr, "%d/%m/%Y").strftime("%d-%m-%Y")
                raw_text = groups[2].rstrip()
                raw_text = raw_text.decode('utf-8')


            label_list.append(label)
            raw_text_list.append(raw_text)
            date_list.append(date)

        for raw_text, label, date in zip(raw_text_list, label_list, date_list):
            if not self.does_raw_text_exist(raw_text):

                row = dict(data_source_id=self._id, genre_friendly=DataUtils.genre_codebook_friendly[label],
                            genre=DataUtils.genre_codebook[label], date=date, article_raw_text=raw_text)
                self.save_raw_to_db(row)
            else:
                count += 1
        print "Found ", count, " duplicate(s) in documents.."


    def apply_preprocessing_and_update_db(self, articles_from_db):
        # apply config and pre-process article

        preprocessor = Preprocessor(self.pre_processing_config)

        if 'nltk' not in self.pre_processing_config.values():
            article_ids, processed_text_list, feature_list = preprocessor.do_parallel_processing(articles_from_db)

            for art_id, processed_text, features in zip(article_ids, processed_text_list, feature_list):
                self.add_features_to_db(art_id, {'article_processed_text': processed_text, 'features':features})

            #make sure the processing is finished
            finished = False
            while not finished:
                if self.get_unprocessed_amount() == 0:
                    finished = True


    def get_number_of_instances(self):
        return DATABASE.get_count(DataSourceConstants.COLLECTION_PROCESSED, {"data_source_id": self._id})

    def get_data_with_labels_from_articles(self, articles):
        dataset = []
        labels = []

        # Get number of examples
        num_examples = len(articles)
        print('Number of examples', num_examples)

        if self.pre_processing_config == None:
            for i, row in enumerate(articles):
                dataset.append(row)
                labels.append([row['genre'], str(row['_id'])])
        else:
            if 'nltk' not in self.pre_processing_config.values():
                # Add features and label for each article
                for i, row in enumerate(articles):
                    sorted_keys = sorted(row['features'].keys())
                    dataset.append([row['features'][f] for f in sorted_keys if f not in DataSourceConstants.NON_FEATURE_COLUMNS])
                    labels.append([row['genre'], str(row['_id'])])
            else:
                for i, row in enumerate(articles):
                    dataset.append(row)
                    labels.append([row['genre'], str(row['_id'])])

        print('Features:', len(dataset))
        print('Labels:', len(labels))
        return dataset, labels

    def get_test_instances(self):
        instances = []

        if not self.training_purpose:
            # For test datasets, the raw text is stored in the X_train variable
            test_articles = dill.loads(DATABASE.getGridFS().get(self.X_train_handler).read())

            for art_raw_text in test_articles:
                art = DataSource.get_processed_article_by_raw_text(art_raw_text)
                instances.append(art)

        else:
            y_test_with_ids = dill.loads(DATABASE.getGridFS().get(self.y_test_with_ids_handler).read())
            test_ids = np.asarray([row[1] for row in y_test_with_ids ])


            for test_id in test_ids:
                instances.append(DataSource.get_processed_article_by_id(test_id))

        return instances

    def get_train_instances(self):
        y_train_with_ids = dill.loads(DATABASE.getGridFS().get(self.y_train_with_ids_handler).read())
        train_ids = np.asarray([row[1] for row in y_train_with_ids])
        instances = []

        for train_id in train_ids:
            instances.append(DataSource.get_processed_article_by_id(train_id))

        return instances

    def apply_grid_search(self):

        from sklearn.model_selection import GridSearchCV
        from sklearn.model_selection import StratifiedKFold
        from sklearn.pipeline import Pipeline
        from sklearn import svm
        from sklearn.linear_model import LogisticRegression
        from sklearn.linear_model import SGDClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.decomposition import PCA
        from sklearn.feature_selection import SelectKBest, chi2
        from sklearn.feature_selection import RFECV
        from sklearn.feature_selection import mutual_info_classif
        from sklearn.ensemble import RandomForestClassifier
        import matplotlib.pyplot as plt
        from sklearn.metrics import classification_report
        import src.data_engineering.utils as DataUtils
        import scipy

        target_names = []
        for number, name in DataUtils.genres.items():
            if 'Unlabelled' not in name:
                target_names.append(''.join(name).split('/')[0])
        print target_names

        X_train = np.asarray(dill.loads(DATABASE.getGridFS().get(self.X_train_handler).read()))
        X_test = np.asarray(dill.loads(DATABASE.getGridFS().get(self.X_test_handler).read()))
        y_train_with_ids = dill.loads(DATABASE.getGridFS().get(self.y_train_with_ids_handler).read())
        y_test_with_ids = dill.loads(DATABASE.getGridFS().get(self.y_test_with_ids_handler).read())
        y_train = np.asarray([row[0] for row in y_train_with_ids])
        y_test = np.asarray([row[0] for row in y_test_with_ids])

        if 'nltk' in self.pre_processing_config.values():
            pickled_model = DATABASE.getGridFS().get(self.vectorizer_handler).read()
            vectorizer = dill.loads(pickled_model)
            X_train = vectorizer.transform(X_train)
            X_test = vectorizer.transform(X_test)

        # Create a pipeline
        pipe = Pipeline([
            # ('reduce_dim', PCA()),
            # ('scale', StandardScaler()),
            ('classify', svm.SVC())
        ])

        # Create space of candidate learning algorithms and their hyperparameters
        N_FEATURES_OPTIONS = [5, 10, 20, 30, 38]
        KERNEL_OPTIONS = ['linear']
        C_OPTIONS = [1, 2, 3, 5, 10]
        # C_OPTIONS = scipy.stats.expon(scale=100)
        # GAMMA_OPTIONS = [1e-3, 1e-4]
        param_grid = [
            # {
            # 'reduce_dim': [PCA()],
            # 'reduce_dim__n_components': N_FEATURES_OPTIONS,
            # 'classify__kernel': KERNEL_OPTIONS,
            # 'classify__C': C_OPTIONS,
            # 'classify__gamma': GAMMA_OPTIONS
            # },
            {
                # 'reduce_dim': [SelectKBest(mutual_info_classif)],
                # 'reduce_dim': [RFECV],
                # 'reduce_dim__k': N_FEATURES_OPTIONS,
                'classify__kernel': KERNEL_OPTIONS,
                'classify__C': C_OPTIONS,
                # 'classify__gamma': GAMMA_OPTIONS
            },
            {
                # 'scale': [StandardScaler()],
                'classify': [SGDClassifier()],
                'classify__loss': ['hinge', 'log'],
                'classify__penalty': ['l2'] ,
            },
            {
                'classify': [RandomForestClassifier()],
                'classify__n_estimators': [10, 100, 1000],
                'classify__max_features': [1, 2, 3, 4, 5, 6]
            },
        ]
        # reducer_labels = ['PCA', 'NMF', 'KBest(chi2)']

        scores = ['accuracy', 'recall_weighted', 'precision_weighted', 'f1_weighted']
        data_table_recommendation = {}
        for score in scores:
            print("# Tuning hyper-parameters for %s" % score)
            print()
            grid = GridSearchCV(pipe, cv=10, n_jobs=1, param_grid=param_grid, scoring=score)
            grid.fit(X_train, y_train)

            print("Best parameters set found on development set:")
            print()
            print(grid.best_params_)
            print()
            print("Grid scores on development set:")
            print()
            means = grid.cv_results_['mean_test_score']
            stds = grid.cv_results_['std_test_score']
            for mean, std, params in zip(means, stds, grid.cv_results_['params']):
                print("%0.3f (+/-%0.03f) for %r"
                      % (mean, std * 2, params))
            print()

            print("Detailed classification report:")
            # print()
            # print("The model is trained on the full development set.")
            # print("The scores are computed on the full evaluation set.")

            y_true, y_pred = y_test, grid.predict(X_test)
            report = classification_report(y_true, y_pred, target_names=target_names)
            print report
            report_dict = DataSource.report_to_df(report).to_dict()
            html_dict = {}
            for measure, gen_val in report_dict.items():
                for genre, value in gen_val.items():
                    # if genre != 'avg/total':
                    if genre not in html_dict.keys():
                        html_dict[genre] = {}
                    html_dict[genre][measure] = value

            print()
            data_table_recommendation[score] = {}
            data_table_recommendation[score]['algorithm'] = grid.best_estimator_.get_params()['classify'].__class__.__name__
            data_table_recommendation[score]['params'] = grid.best_params_
            data_table_recommendation[score]['report'] = html_dict


            print("Best model and parameters")
            print(grid.best_estimator_.get_params()['classify'])

        feature_reduction_data = {}
        if 'nltk' not in self.pre_processing_config.values():
            rfecv = RFECV(estimator=LogisticRegression(), step=1, cv=StratifiedKFold(10),
                          scoring='accuracy')
            rfecv.fit(X_train, y_train)

            print("Optimal number of features : %d" % rfecv.n_features_)
            print("Optimal features :")
            selected = rfecv.get_support()
            indices = []
            ind = 0
            print selected
            for b in selected:
                if not b:
                    indices.append(ind)
                ind += 1

            sorted_keys = sorted(DataUtils.features)
            print sorted_keys
            f_names = [f for f in sorted_keys if f not in DataSourceConstants.NON_FEATURE_COLUMNS]

            print ("Non-Selected features are:")
            print (np.array(f_names)[indices])
            feature_reduction_data['non-selected'] = np.array(f_names)[indices]
            feature_reduction_data['selected'] = rfecv.get_support()
            feature_reduction_data['optimal_number'] = rfecv.n_features_

        return data_table_recommendation, feature_reduction_data

    @staticmethod
    def report_to_df(report):
        import pandas as pd
        report = re.sub(r" +", " ", report).replace("avg / total", "avg/total").replace("\n ", "\n")
        report_df = pd.read_csv(StringIO("Classes" + report), sep=' ', index_col=0)
        print report_df.to_dict()
        return (report_df)
        # dataframe.to_csv('classification_report.csv', index=False)


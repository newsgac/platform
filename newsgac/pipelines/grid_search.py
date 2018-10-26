import numpy
from sklearn.model_selection import GridSearchCV

from newsgac import config
from newsgac.learners import learners, GridSearch, LearnerSVC, LearnerNB
from newsgac.pipelines.get_sk_pipeline import get_sk_pipeline
from newsgac.tasks.progress import report_progress

param_space = {
    LearnerSVC: {
        'kernel': ['linear'],
        'C': [1, 2, 3, 5, 10],
        'gamma': [1e-1, 1e-2, 1e-3],
    },
    LearnerNB: {
        'alpha': [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
    },
}

def run_grid_search(pipeline):
    texts = numpy.array([article.raw_text for article in pipeline.data_source.articles])
    labels = numpy.array([article.label for article in pipeline.data_source.articles])

    pipeline.grid_search_result = {}

    for learner in learners:
        if learner in param_space:
            report_progress('gridsearch/%s' % learner.tag, 0)
            skp = get_sk_pipeline(pipeline.sw_removal, pipeline.lemmatization, pipeline.nlp_tool, learner.create())
            space = {
                'Classifier__%s' % name: space for name, space in param_space[learner].iteritems()
            }
            search = GridSearchCV(skp, space, iid=False, cv=5, return_train_score=False, n_jobs=config.n_parallel_jobs)
            search.fit(texts, labels)
            print("Best parameter (CV score=%0.3f):" % search.best_score_)
            print(search.best_params_)
            report_progress('gridsearch/%s' % learner.tag, 1)

            pipeline.grid_search_result[learner.tag] = {
                'full': search.cv_results_,
                'best': search.best_params_
            }

    pipeline.save()




# #KERNEL_OPTIONS = ['linear', 'rbf']
#         C_OPTIONS = [1, 2, 3, 5, 10]
#         # C_OPTIONS = scipy.stats.expon(scale=100)
#         GAMMA_OPTIONS = [1e-1, 1e-2, 1e-3]
#         param_grid = [
#             # {
#             # 'reduce_dim': [PCA()],
#             # 'reduce_dim__n_components': N_FEATURES_OPTIONS,
#             # 'classify__kernel': KERNEL_OPTIONS,
#             # 'classify__C': C_OPTIONS,
#             # 'classify__gamma': GAMMA_OPTIONS
#             # },
#             {
#                 # 'reduce_dim': [SelectKBest(mutual_info_classif)],
#                 # 'reduce_dim': [RFECV],
#                 # 'reduce_dim__k': N_FEATURES_OPTIONS,
#                 'classify__kernel': KERNEL_OPTIONS,
#                 'classify__C': C_OPTIONS,
#                 'classify__gamma': GAMMA_OPTIONS,
#             },
#             # {
#             #     # 'scale': [StandardScaler()],
#             #     'classify': [MultinomialNB()],
#             #     'classify__alpha': [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
#             #     # 'classify__penalty': ['l2'] ,
#             # },
#             {
#                 'classify': [RandomForestClassifier()],
#                 'classify__criterion':['gini'],
#                 'classify__n_estimators': [50, 100, 250, 500, 1000],
#                 'classify__max_features': [1, 2, 3, 4, 5, 6],
#                 # 'classify__max_depth': [1, 5, 10, 15, 20, 25, 30],
#                 # 'classify__min_samples_leaf': [1, 2, 4, 6, 8, 10],
#             },
#
#             {
#                 'classify': [XGBClassifier()],
#                 'classify__n_estimators': [50, 100, 250, 500, 1000],
#                 'classify__max_depth': [1, 2, 3, 4, 5, 10],
#                 'classify__learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2],
#             },
#         ]
import numpy
from time import time
from sklearn.model_selection import GridSearchCV

from newsgac import config
from newsgac.learners import learners, LearnerSVC, LearnerNB, LearnerXGB, LearnerGB, LearnerMLP, LearnerRF, LearnerLGBM
from newsgac.pipelines.get_sk_pipeline import get_sk_pipeline
from newsgac.pipelines.utils import report

param_space = {
    # TODO: mostly commented during dev
    LearnerSVC: {
        'kernel': ['linear', 'rbf'],
        'C': [0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 3, 4],          # increasing C values may lead to overfitting
        'gamma': [1e-1, 1e-2, 1e-3],    # increasing gamma leads to overfitting
        # 'tol': [1e-2, 1e-3, 1e-4, 1e-5, 1e-6],
        # 'class_weight': [None, 'balanced'],
    },
    LearnerNB: {
        'alpha': [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
    },
    LearnerRF: {
        'criterion': ['gini', 'entropy'],
        'n_estimators': [10, 30, 50, 100, 120, 160],
        'max_features': [None, 2, 4, 6, 8, 12, 24],
        'max_depth': [None, 2, 4, 6, 8, 10, 12],
        # 'min_samples_split': [2, 4, 8, 16, 32],
        'min_samples_leaf': [1, 3, 5, 7, 9],          # tune
        # 'max_leaf_nodes': [None, 4, 6, 8, 16, 32, 64],
        # 'class_weight': [None, 'balanced'],
    },
    # LearnerGB: {
    #     'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.5],
    #     'n_estimators' : [1, 2, 4, 8, 16, 32, 64],
    #     'max_depth': numpy.linspace(1, 32, 32, endpoint=True),
    #     'loss': ['deviance', 'exponential'],
    #     'max_features': [1, 2, 3, 4, 5, 6, 'sqrt', 'log2', 'auto', 0.5],
    #
    # },
    # LearnerXGB: {
    #     'min_child_weight': [1, 2, 5, 10],
    #     'gamma': [0, 0.5, 1, 1.5, 2, 5],
    #     'learning_rate': [0.01, 0.05, 0.1, 0.2],
    #     'subsample': [0.4, 0.6, 0.8, 1.0],
    #     'colsample_bytree': [0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 1.0],
    #     'max_depth': [0, 1, 3, 4, 5, 6, 8, 10],
    #     'n_estimators': [75, 100, 150, 200],
    #     'scale_pos_weight': [0.01, 0.05, 0.06, 0.1, 0.6, 0.8, 1.0]
    #
    # },
    LearnerLGBM: {
        'objective': ['multiclass'],
        'metric': ['multi_logloss'],
        'silent': [True],
        'n_estimators': [10, 30, 50, 100, 120, 160],
        'max_depth': [-1, 0, 2, 4, 8],
        'boosting_type': ['gbdt', 'dart', 'goss', 'rf'],
        'num_leaves': [2, 4, 8, 16, 32, 64, 128],
        'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.5],
        # 'max_bin': [32, 64, 128, 255],
        # 'min_data_in_leaf': [2, 4, 8, 16, 32, 64, 128],
        # 'min_sum_hessian_in_leaf': [1e-1, 1e-2, 1e-3, 1e-4, 1e-5],
        # 'bagging_fraction': [0.1, 0.2, 0.3, 0.6, 0.8, 1.0],
        # 'feature_fraction': [0.1, 0.2, 0.3, 0.6, 0.8, 1.0],
        # 'lambda_l1': [0, 0.05, 0.1, 0.3, 0.8, 1.0],
        # 'lambda_l2': [0, 0.05, 0.1, 0.3, 0.8, 1.0],
        # 'min_gain_to_split': [0, 0.05, 0.1, 0.3, 0.8, 1.0],
        # 'bagging_freq': [0, 2, 4, 8, 16, 32],
        # 'learning_rate': [0.01, 0.05, 0.1, 0.2],
        # 'class_weight': [None, 'balanced'],
        # 'scale_pos_weight': [0.01, 0.06, 0.1, 0.2, 0.3, 0.6, 0.8, 1.0]
    },

    LearnerMLP:{
        'activation': ['relu', 'logistic', 'tanh'],
        'alpha': [1e-06, 1e-05, 1e-03, 1e-01],
        'batch_size': ['auto', 50, 100, 300],
        # 'early_stopping': [True],
        'hidden_layer_sizes': [(5, 2), (15, 20), (50, 50), (100, 100)],
        'learning_rate': ['constant', 'adaptive'],
        'max_iter': [80, 100, 200],
        'n_iter_no_change': [5, 10, 15],
        # 'random_state': [1],
        # 'shuffle': [True],
        # 'solver': ['adam'],
    },
}


def run_grid_search(pipeline):
    texts = numpy.array([article.raw_text for article in pipeline.data_source.articles])
    labels = numpy.array([article.label for article in pipeline.data_source.articles])
    param_grid = []
    pipeline.grid_search_result = {}
    scores = ['accuracy', 'recall_micro', 'precision_micro', 'f1_micro']
    for learner in learners:
        if learner in param_space:
            space = {
                'Classifier__%s' % name: space for name, space in param_space[learner].items()
            }
            space['Classifier'] = [learner.create().get_classifier()]
            param_grid.append(space)

    # print param_grid
    # add dummy learner
    # TODO: this is ultra automated but also takes a long time, how about we put an optimized checkbox for the rest of the algortihms to do GS per alg
    skp = get_sk_pipeline(pipeline)
    search = GridSearchCV(skp, param_grid, cv=5, return_train_score=False, n_jobs=config.n_parallel_jobs,
                          scoring=scores[3])
    start = time()
    search.fit(texts, labels)
    print(("Best parameter (CV score=%0.3f):" % search.best_score_))
    print((search.best_params_))

    pipeline.grid_search_result = {
        'full': search.cv_results_,
        'best': search.best_params_
    }
    print(pipeline.grid_search_result)
    print(("GridSearchCV took %.2f seconds for %d candidate parameter settings."
          % (time() - start, len(search.cv_results_['params']))))
    report(search.cv_results_)

    pipeline.save()

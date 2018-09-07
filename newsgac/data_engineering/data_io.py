'''The data input/output operations'''
import csv
import os
import numpy as np
from newsgac.data_engineering import utils

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../datasets/')

'''Adapted from https://github.com/jlonij/genre-classifier/blob/master/data.py'''
def load_preprocessed_data_from_file(filename):
    '''
    Transform tabular data_sources set into NumPy arrays.
    '''
    # Load training data_sources from csv file
    with open(DATA_DIR+filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')

        # Get number of examples
        num_examples = sum(1 for row in reader)
        print('Number of examples', num_examples)

        # Get number of features
        num_features = len(utils.features)
        print('Number of features', num_features)

        dataset = np.ndarray(shape=(num_examples, num_features),
                             dtype=np.float64)
        labels = np.ndarray(shape=(num_examples,), dtype=np.int32)

        # Add features and label for each article
        csvfile.seek(0)
        reader.next()
        for i, row in enumerate(reader):
            dataset[i, :] = [row[f] for f in sorted(utils.features)]
            labels[i] = row['label']

        print('Features:', dataset.shape)
        print('Labels:', labels.shape)
        return dataset, labels

def strip_data_row(data, experiment):
    # strip the data according to the experiment features
    selected_features = experiment.features.keys()
    # non_feature_columns = ['_id', 'date', 'genre', 'genre_friendly', 'article_raw_text', 'data_source_id']
    res = [[data['features'][f] for f in sorted(data['features'].keys()) if f in selected_features]]
    return res

def get_feature_names():
    non_feature_columns = ['_id', 'date', 'genre', 'genre_friendly', 'article_raw_text', 'data_source_id']
    return [f for f in sorted(utils.features) if f not in non_feature_columns]

def get_feature_names_with_descriptions():
    non_feature_columns = ['_id', 'date', 'genre', 'genre_friendly', 'article_raw_text', 'data_source_id']
    new_dict = {}
    for f in sorted(utils.features):
        if f not in non_feature_columns:
            new_dict[f] = utils.feature_descriptions[f]
    return new_dict


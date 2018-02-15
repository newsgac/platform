'''The data input/output operations'''
import csv
import os, sys
import numpy as np
from src.data_engineering import utils
from src.common.database import Database
from src.models.data_sources.data_source import DataSource

DATABASE = Database()
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
            dataset[i, :] = [row[f] for f in utils.features]
            labels[i] = row['label']

        print('Features:', dataset.shape)
        print('Labels:', labels.shape)
        return dataset, labels


#TODO: test this method
def load_preprocessed_data_from_db(data_source_id):

    non_feature_columns = ['_id', 'date', 'genre', 'genre_friendly' 'article_raw_text', 'data_source_id']
    articles = DataSource.get_articles_by_data_source(data_source_id)

    # Get number of examples
    num_examples = len(articles)
    print('Number of examples', num_examples)

    # Get number of features
    num_features = len(articles[0].keys()) - len(non_feature_columns)
    print('Number of features', num_features)

    dataset = np.ndarray(shape=(num_examples, num_features),
                         dtype=np.float64)
    labels = np.ndarray(shape=(num_examples, 2), dtype=np.int32)

    # Add features and label for each article

    for i, row in enumerate(articles):
        dataset[i, :] = [row[f] for f in articles[i].keys() if f not in non_feature_columns]
        labels[i] = [row['genre'], row['_id']]

    print('Features:', dataset.shape)
    print('Labels:', labels.shape)
    return dataset, labels


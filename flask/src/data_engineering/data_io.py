'''The data input/output operations'''
import csv
import os
import numpy as np
from data_engineering import utils

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../../data/')

'''Adapted from https://github.com/jlonij/genre-classifier/blob/master/data.py'''
def load_data(filename):
    '''
    Transform tabular data set into NumPy arrays.
    '''
    # Load training data from csv file
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

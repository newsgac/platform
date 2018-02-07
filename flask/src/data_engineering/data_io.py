'''The data input/output operations'''
import csv
import os

import datetime
import numpy as np
from dill import dill
import pickle
import re

from data_engineering import utils
from src.common.database import Database

DATABASE = Database()


DATA_DIR = os.path.join(os.path.dirname(__file__), '../../../data_sources/')

'''Adapted from https://github.com/jlonij/genre-classifier/blob/master/data_sources.py'''
def load_preprocessed_data(filename):
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

def read_and_upload_raw_text_input_file(ds):

    file = DATABASE.getGridFS().get(ds.file_handler_db).read()
    data = []

    for line in file.splitlines():
        line = line.rstrip()

        # groups = re.search(r'^__label__(.{3}.+)DATE\=([\0-9]+) ((?s).*)$', line).groups()
        # groups = re.search(r'^__label__(.{3}.+)DATE\=([\0-9]+[^&]) ((?s).*)$', line).groups()
        groups = re.search(r'^__label__(.{3}.+)DATE\=(.{8}) ((?s).*)$', line).groups()

        if not groups:
            groups = re.search(r'^__label__(.{3})((?s).*)', line).groups()
            label = groups[0].rstrip()
            date = None
            raw_text = groups[1].rstrip()
        else:
            label = groups[0].rstrip()
            date_str = groups[1].rstrip()
            print date_str
            date = datetime.datetime.strptime(date_str, "%d/%m/%y").strftime("%d-%m-%Y")
            raw_text = groups[2].rstrip()

        row = dict(data_source_id=ds._id, genre=utils.genre_codebook[label], date=date, article_raw_text=raw_text)
        ds.save_raw_to_db(row)
        data.append(row)

    return data

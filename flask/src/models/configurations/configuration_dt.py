import uuid
import src.models.configurations.constants as ConfigurationConstants
import src.models.configurations.errors as ConfigurationErrors
from src.common.database import Database

DATABASE = Database()

__author__ = 'abilgin'

class ConfigurationDT():

    def __init__(self, user_email, **kwargs):

        if 'form' in kwargs:
            # creation from the web
            self.user_email = user_email
            self._id = uuid.uuid4().hex
            self.type = "DT"
            self.render_form(kwargs['form'])
        elif 'configuration' in kwargs:
            # request from the creation of experiment
            self.__dict__.update(kwargs['configuration'].__dict__)
            self.user_email = user_email
        else:
            # default constructor from the database
            self.__dict__.update(kwargs)
            self.user_email = user_email


    def __eq__(self, other):

        if other is None:
            return False

        if self.type != other.type:
            return False

        return self.stemming == other.stemming and self.sw_removal == other.sw_removal and self.avg_sent_length == other.avg_sent_length and \
                self.avg_sent_length == other.avg_sent_length and self.perc_exclamation_mark == other.perc_exclamation_mark and \
                self.perc_adjectives == other.perc_adjectives and self.criterion == other.criterion and self.splitter == other.splitter and \
                self.min_samples_split == other.min_samples_split and self.min_samples_leaf == other.min_samples_leaf and \
                self.max_features == other.max_features and self.random_state == other.random_state


    def render_form(self, form):

        # pre-processing and feature selection
        self.auto_pp = "auto_pp" in form

        if self.auto_pp:
            self.stemming = False
            self.sw_removal = False
            self.avg_sent_length = False
            self.perc_exclamation_mark = False
            self.perc_adjectives = False
        else:
            self.stemming = 'stemming' in form
            self.sw_removal = 'sw_removal' in form
            self.avg_sent_length = 'avg_sent_length' in form
            self.perc_exclamation_mark = 'perc_exclamation_mark' in form
            self.perc_adjectives = 'perc_adjectives' in form

        # algorithm specific parameters
        self.auto_alg = "auto_alg" in form

        if self.auto_alg:
            self.criterion = ConfigurationConstants.DT_DEFAULT_CRITERION
            self.splitter = ConfigurationConstants.DT_DEFAULT_SPLITTER
            self.min_samples_split = ConfigurationConstants.DT_DEFAULT_MIN_SAMPLES_SPLIT
            self.min_samples_leaf = ConfigurationConstants.DT_DEFAULT_MIN_SAMPLES_LEAF
            self.max_features = ConfigurationConstants.DT_DEFAULT_MAX_FEATURES
            self.random_state = ConfigurationConstants.DT_DEFAULT_RANDOM_STATE
        else:
            self.criterion = form['criterion'] if 'criterion' in form else ConfigurationConstants.DT_DEFAULT_CRITERION
            self.splitter = form['splitter'] if 'splitter' in form else ConfigurationConstants.DT_DEFAULT_SPLITTER

            try:
                val = int(form['min_samples_split'])
            except ValueError:
                try:
                    val = float(form['min_samples_split'])
                except ValueError:
                    val = ConfigurationConstants.DT_DEFAULT_MIN_SAMPLES_SPLIT

            self.min_samples_split = val

            try:
                val = int(form['min_samples_leaf'])
            except ValueError:
                try:
                    val = float(form['min_samples_leaf'])
                except ValueError:
                    val = ConfigurationConstants.DT_DEFAULT_MIN_SAMPLES_LEAF

            self.min_samples_leaf = val

            try:
                val = int(form['max_features'])
            except ValueError:
                try:
                    val = float(form['max_features'])
                except ValueError:
                    if not form['max_features'] in ["auto", "log2", "sqrt"]:
                        val = ConfigurationConstants.DT_DEFAULT_MAX_FEATURES

            self.max_features = val

            try:
                val = int(form['random_state'])
            except ValueError:
                val = ConfigurationConstants.DT_DEFAULT_RANDOM_STATE

            self.random_state = val

    @classmethod
    def get_by_user_email(cls, user_email):
        return [cls(**elem) for elem in DATABASE.find(ConfigurationConstants.COLLECTION, {"user_email": user_email})]

    @staticmethod
    def is_config_unique(new_config):
        user_config_list = ConfigurationDT.get_by_user_email(new_config.user_email)

        for config in user_config_list:
            if config == new_config:
                raise ConfigurationErrors.ConfigAlreadyExistsError("The configuration already exists.")

        return True

    def save_to_db(self):
        DATABASE.update(ConfigurationConstants.COLLECTION, {"_id": self._id}, self.__dict__)

    def delete(self):
        DATABASE.remove(ConfigurationConstants.COLLECTION, {"_id": self._id})



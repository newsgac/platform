import uuid
import src.models.configurations.constants as ConfigurationConstants
import src.models.configurations.errors as ConfigurationErrors
from src.database import DATABASE
from src.models.data_sources.data_source import DataSource
import src.data_engineering.data_io as DataIO

__author__ = 'abilgin'

class ConfigurationMLP():

    def __init__(self, user_email, **kwargs):

        if 'form' in kwargs:
            # creation from the web
            self.user_email = user_email
            self._id = uuid.uuid4().hex
            self.type = "MLP"
            self.features = {}
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

        return self.features == other.features and self.alpha == other.alpha and  \
                self.data_source_id == other.data_source_id

    def render_form(self, form):

        if form["data_source"]:
            ds = DataSource.get_by_user_email_and_display_title(self.user_email, form["data_source"])
            self.data_source_id = ds._id
            self.data_source_title = ds.display_title
            if 'tf-idf' in ds.pre_processing_config.values():
                self.auto_feat = True
            else:
                # pre-processing and feature selection
                self.auto_feat = "auto_feat" in form

                manual_feature_dict = DataIO.get_feature_names_with_descriptions()

                if self.auto_feat:
                    for feature in sorted(manual_feature_dict.keys()):
                        self.features[feature] = True
                else:
                    for feature in sorted(manual_feature_dict.keys()):
                        if feature in form:
                            self.features[feature] = feature in form
        else:
            self.data_source_id = None
            self.data_source_title = None

        # algorithm specific parameters
        self.auto_alg = "auto_alg" in form

        if self.auto_alg:
            self.alpha = ConfigurationConstants.MLP_DEFAULT_ALPHA
        else:

            try:
                val = float(form['alpha'])
            except ValueError:
                val = ConfigurationConstants.MLP_DEFAULT_ALPHA

            self.alpha = val


    @classmethod
    def get_by_user_email(cls, user_email):
        return [cls(**elem) for elem in DATABASE.find(ConfigurationConstants.COLLECTION, {"user_email": user_email, "type":"MLP"})]

    @staticmethod
    def is_config_unique(new_config):
        user_config_list = ConfigurationMLP.get_by_user_email(new_config.user_email)

        for config in user_config_list:
            if config == new_config:
                raise ConfigurationErrors.ConfigAlreadyExistsError("The configuration already exists.")

        return True

    def save_to_db(self):
        DATABASE.update(ConfigurationConstants.COLLECTION, {"_id": self._id}, self.__dict__)

    def delete(self):
        DATABASE.remove(ConfigurationConstants.COLLECTION, {"_id": self._id})



from pymodm import fields, EmbeddedMongoModel
from sklearn.neural_network import MLPClassifier

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    alpha = fields.FloatField(default=0.0001)


class LearnerMLP(Learner):
    name = 'Multi-Layer Perceptron'
    tag = 'mlp'
    parameters = fields.EmbeddedDocumentField(Parameters)

    def get_classifier(self):
        return MLPClassifier(
            hidden_layer_sizes = (100,),
            activation = "relu",
            solver = 'adam',
            alpha = self.parameters.alpha,
            batch_size = 'auto',
            learning_rate = "constant",
            learning_rate_init = 0.001,
            power_t = 0.5,
            max_iter = 200,
            shuffle = True,
            random_state = 42,
            tol = 1e-4,
            verbose = False,
            warm_start = False,
            momentum = 0.9,
            nesterovs_momentum = True,
            early_stopping = True,
            validation_fraction = 0.1,
            beta_1 = 0.9,
            beta_2 = 0.999,
            epsilon = 1e-8,
            n_iter_no_change = 10,
        )

from pymodm import fields, EmbeddedMongoModel
from sklearn.neural_network import MLPClassifier

from .learner import Learner


class Parameters(EmbeddedMongoModel):
    alpha = fields.FloatField(default=0.0001)
    alpha.description = 'L2 penalty (regularization term) parameter.'

    solver =  fields.CharField(
        verbose_name="Solver",
        required=False,
        default='adam',
        choices=[
            ('lbfgs', 'lbfgs'),
            ('adam', 'adam'),
            ('sgd', 'sgd'),
        ]
    )
    solver.description = 'The solver for weight optimization.'

    activation = fields.CharField(
        verbose_name="Activation function",
        required=False,
        default='relu',
        choices=[
            ('identity', 'identity'),
            ('logistic', 'logistic'),
            ('tanh', 'tanh'),
            ('relu', 'relu'),
        ]
    )
    activation.description = 'Activation function for the hidden layer.'

    max_iter = fields.IntegerField(required=False, default=200)
    max_iter.description = 'Maximum number of iterations.'

    batch_size = fields.IntegerField(required=False, default=200)
    batch_size.description = 'Size of minibatches for stochastic optimizers.'

    learning_rate = fields.CharField(
        verbose_name="Learning rate",
        required=False,
        default='constant',
        choices=[
            ('constant', 'Constant'),
            ('invscaling', 'Inverse scaling'),
            ('adaptive', 'Adaptive'),
        ]
    )
    learning_rate.description = 'Learning rate schedule for weight updates.'

    hidden_layer_sizes =  fields.CharField(
        verbose_name="Hidden layer sizes",
        required=False,
        default='100',
        # choices=[
        #     ('100', 'Default'),
        #     ('200, 100', '(200, 100)'),
        #     ('30, 10', '(30, 10)'),
        #     ('10, 30', '(10, 30)'),
        # ]
    )
    hidden_layer_sizes.description = 'Activation function for the hidden layer. Enter an integer per layer separated by a comma.'

class LearnerMLP(Learner):
    name = 'Multi-Layer Perceptron'
    tag = 'mlp'
    parameters = fields.EmbeddedDocumentField(Parameters)

    @staticmethod
    def transform_hidden_layer_to_tuple(str_layers):
        layers = str_layers.split(',')
        layers_int = [int(l) for l in layers]
        return tuple(layers_int)

    def get_classifier(self):
        return MLPClassifier(
            hidden_layer_sizes = self.transform_hidden_layer_to_tuple(self.parameters.hidden_layer_sizes),
            activation = self.parameters.activation,
            solver = self.parameters.solver,
            alpha = self.parameters.alpha,
            batch_size = self.parameters.batch_size,
            learning_rate = self.parameters.learning_rate,
            max_iter = self.parameters.max_iter,

            learning_rate_init = 0.001,
            power_t = 0.5,
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

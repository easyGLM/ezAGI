# SimpleMind.py (c) 2024 Gregory L. Magnusson MIT licence
# minimalistic neural network in JAX
# creates long term memory adaptation as learning for easyAGI

import os
import jax.numpy as jnp
import jax.random as random
import optax
from jax import grad, jit
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

class SimpleMind:
    def __init__(self, input_size, hidden_sizes, output_size, activation='relu', optimizer='adam', learning_rate=0.001, regularization=None, reg_lambda=0.01):
        """
        Initialize the SimpleMind neural network.

        :param input_size: Size of the input layer.
        :param hidden_sizes: List of sizes for hidden layers.
        :param output_size: Size of the output layer.
        :param activation: Activation function to use ('relu', 'sigmoid', 'tanh').
        :param optimizer: Optimizer to use ('adam', 'sgd').
        :param learning_rate: Learning rate for training.
        :param regularization: Regularization method ('l2').
        :param reg_lambda: Regularization strength.
        """
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        self.activation = activation
        self.optimizer_name = optimizer
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.reg_lambda = reg_lambda
        self.rng = random.PRNGKey(0)
        
        self.params = self._initialize_parameters()
        self.opt_state = self._initialize_optimizer()
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def _initialize_parameters(self):
        """
        Initialize the parameters of the network.

        :return: Dictionary of initialized parameters.
        """
        layer_sizes = [self.input_size] + self.hidden_sizes + [self.output_size]
        params = {}
        for i in range(len(layer_sizes) - 1):
            self.rng, layer_rng = random.split(self.rng)
            params[f'W{i}'] = random.normal(layer_rng, (layer_sizes[i], layer_sizes[i+1])) * 0.01
            params[f'b{i}'] = jnp.zeros(layer_sizes[i+1])
        return params

    def _initialize_optimizer(self):
        """
        Initialize the optimizer state.

        :return: Initialized optimizer state.
        """
        if self.optimizer_name == 'adam':
            optimizer = optax.adam(self.learning_rate)
        elif self.optimizer_name == 'sgd':
            optimizer = optax.sgd(self.learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {self.optimizer_name}")
        return optimizer.init(self.params)

    def _activation_function(self, s):
        if self.activation == 'sigmoid':
            return 1 / (1 + jnp.exp(-s))
        elif self.activation == 'tanh':
            return jnp.tanh(s)
        elif self.activation == 'relu':
            return jnp.maximum(0, s)
        else:
            raise ValueError("Unsupported activation function.")

    def forward(self, X):
        """
        Perform a forward pass through the network.

        :param X: Input data.
        :return: Output of the network.
        """
        out = X
        for i in range(len(self.hidden_sizes)):
            W, b = self.params[f'W{i}'], self.params[f'b{i}']
            out = jnp.dot(out, W) + b
            out = self._activation_function(out)
        W, b = self.params[f'W{len(self.hidden_sizes)}'], self.params[f'b{len(self.hidden_sizes)}']
        out = jnp.dot(out, W) + b
        return out

    @jit
    def _loss_fn(self, params, X, y):
        def loss(params):
            predictions = self.forward(X)
            loss_value = jnp.mean((predictions - y) ** 2)
            if self.regularization == 'l2':
                l2_penalty = sum(jnp.sum(jnp.square(params[f'W{i}'])) for i in range(len(self.hidden_sizes) + 1))
                loss_value += self.reg_lambda * l2_penalty / 2
            return loss_value
        return loss(params)

    @jit
    def _gradient_fn(self, params, X, y):
        return grad(self._loss_fn)(params, X, y)

    def _parallel_backpropagate(self, X, y):
        """
        Perform backpropagation in parallel using multiple threads.
        """
        def worker(X, y):
            return self._backpropagate(X, y)

        with ThreadPoolExecutor(os.cpu_count()) as executor:
            futures = [executor.submit(worker, X[i], y[i]) for i in range(len(X))]

        results = []
        for future in as_completed(futures):
            results.append(future.result())
        return results

    @jit
    def _backpropagate(self, X, y):
        grads = self._gradient_fn(self.params, X, y)
        updates, self.opt_state = self.optimizer.update(grads, self.opt_state)
        self.params = optax.apply_updates(self.params, updates)
        return self.params, self.opt_state

    def train(self, X, y, epochs):
        """
        Train the network on the given data.

        :param X: Input data.
        :param y: Target labels.
        :param epochs: Number of epochs to train.
        """
        for epoch in range(epochs):
            self._parallel_backpropagate(X, y)
            if epoch % 100 == 0:
                loss_value = self._calculate_loss(X, y)
                logging.info(f"Epoch {epoch}, Loss: {loss_value}")

    @jit
    def _calculate_loss(self, X, y):
        """
        Calculate the loss of the network.
        """
        output = self.forward(X)
        loss_value = jnp.mean(jnp.square(y - output))
        if self.regularization == 'l2':
            loss_value += self.reg_lambda / 2 * sum(jnp.sum(jnp.square(self.params[f'W{i}'])) for i in range(len(self.hidden_sizes) + 1))
        return loss_value

# Example usage
if __name__ == "__main__":
    input_size = 4
    hidden_sizes = [10, 10]
    output_size = 1
    learning_rate = 0.001
    epochs = 1000

    X = jnp.array([[1.0, 2.0, 3.0, 4.0]])
    y = jnp.array([[1.0]])

    simple_mind = SimpleMind(input_size, hidden_sizes, output_size, activation='relu', optimizer='adam', learning_rate=learning_rate, regularization='l2', reg_lambda=0.01)
    simple_mind.train(X, y, epochs)
    print("Final output:", simple_mind.forward(X))


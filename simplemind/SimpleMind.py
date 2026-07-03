# SimpleMind.py (c) 2024 Gregory L. Magnusson MIT licence
# minimalistic neural network in JAX
# creates long term memory adaptation as learning for easyAGI

import os
import logging

# jax/optax are optional heavy dependencies. Guard the imports so that
# `import simplemind.SimpleMind` succeeds even when they are not installed;
# a helpful error is raised only when SimpleMind is actually constructed.
try:
    import jax.numpy as jnp
    import jax.random as random
    import optax
    from jax import grad, jit
    _JAX_AVAILABLE = True
    _JAX_IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover - exercised only without jax
    jnp = None
    random = None
    optax = None
    grad = None
    jit = None
    _JAX_AVAILABLE = False
    _JAX_IMPORT_ERROR = _e


def _require_jax():
    """Raise a helpful install hint when jax/optax are unavailable."""
    if not _JAX_AVAILABLE:
        raise ImportError(
            "SimpleMind requires jax and optax. Install the learning extras "
            'with: pip install "ezagi[learn]"'
        ) from _JAX_IMPORT_ERROR


# ---------------------------------------------------------------------------
# Module-level pure functions. These take params explicitly (no `self`) so
# they can be jitted cleanly. The network topology (hidden_sizes, activation,
# regularization) is passed as data / closed over where needed.
# ---------------------------------------------------------------------------

def _activation_function(s, activation):
    if activation == 'sigmoid':
        return 1 / (1 + jnp.exp(-s))
    elif activation == 'tanh':
        return jnp.tanh(s)
    elif activation == 'relu':
        return jnp.maximum(0, s)
    else:
        raise ValueError("Unsupported activation function.")


def _forward(params, x, num_hidden, activation):
    """Pure forward pass over an MLP described by `params`."""
    out = x
    for i in range(num_hidden):
        W, b = params[f'W{i}'], params[f'b{i}']
        out = jnp.dot(out, W) + b
        out = _activation_function(out, activation)
    W, b = params[f'W{num_hidden}'], params[f'b{num_hidden}']
    out = jnp.dot(out, W) + b
    return out


def _loss(params, x, y, num_hidden, activation, regularization, reg_lambda):
    """Mean-squared-error loss with optional L2 regularization."""
    predictions = _forward(params, x, num_hidden, activation)
    loss_value = jnp.mean((predictions - y) ** 2)
    if regularization == 'l2':
        l2_penalty = sum(
            jnp.sum(jnp.square(params[f'W{i}'])) for i in range(num_hidden + 1)
        )
        loss_value = loss_value + reg_lambda * l2_penalty / 2
    return loss_value


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
        _require_jax()

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

        # Store the optimizer and its state on the instance. optax optimizer
        # objects are not clean jit arguments, so we close over self.optimizer
        # inside jitted update/loss closures built here in __init__.
        self.optimizer = self._make_optimizer()
        self.opt_state = self.optimizer.init(self.params)

        self._build_jitted_functions()
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def _make_optimizer(self):
        if self.optimizer_name == 'adam':
            return optax.adam(self.learning_rate)
        elif self.optimizer_name == 'sgd':
            return optax.sgd(self.learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {self.optimizer_name}")

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

    def _build_jitted_functions(self):
        """Construct jitted closures over the (static) network config and the
        optax optimizer, avoiding passing self/optimizer as jit arguments."""
        num_hidden = len(self.hidden_sizes)
        activation = self.activation
        regularization = self.regularization
        reg_lambda = self.reg_lambda
        optimizer = self.optimizer

        @jit
        def forward_fn(params, x):
            return _forward(params, x, num_hidden, activation)

        @jit
        def loss_fn(params, x, y):
            return _loss(params, x, y, num_hidden, activation,
                         regularization, reg_lambda)

        grad_fn = jit(grad(loss_fn))

        @jit
        def update_fn(params, opt_state, x, y):
            grads = grad_fn(params, x, y)
            updates, opt_state = optimizer.update(grads, opt_state)
            params = optax.apply_updates(params, updates)
            return params, opt_state

        self._forward_fn = forward_fn
        self._loss_fn = loss_fn
        self._update_fn = update_fn

    def forward(self, X):
        """
        Perform a forward pass through the network.

        :param X: Input data.
        :return: Output of the network.
        """
        return self._forward_fn(self.params, X)

    # predict is a public alias for forward for API clarity.
    def predict(self, X):
        return self.forward(X)

    def train(self, X, y, epochs):
        """
        Train the network on the given data.

        :param X: Input data.
        :param y: Target labels.
        :param epochs: Number of epochs to train.
        """
        for epoch in range(epochs):
            self.params, self.opt_state = self._update_fn(
                self.params, self.opt_state, X, y
            )
            if epoch % 100 == 0:
                loss_value = self._loss_fn(self.params, X, y)
                logging.info(f"Epoch {epoch}, Loss: {loss_value}")


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

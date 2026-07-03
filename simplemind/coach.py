# coach.py (c) 2024 Gregory L. Magnusson MIT licence
# trainer for SimpleMind neural network
import os
import json
import logging
import time
import pickle
from simplemind.SimpleMind import SimpleMind

# jax/optax are optional heavy dependencies; guard so importing coach works
# without them. Construction of SimpleMind will raise the helpful install hint.
try:
    import jax.numpy as jnp
    _JAX_AVAILABLE = True
    _JAX_IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover - exercised only without jax
    jnp = None
    _JAX_AVAILABLE = False
    _JAX_IMPORT_ERROR = _e


def _require_jax():
    if not _JAX_AVAILABLE:
        raise ImportError(
            "coach requires jax and optax. Install the learning extras with: "
            'pip install "ezagi[learn]"'
        ) from _JAX_IMPORT_ERROR

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Coach')

STM_FOLDER = './memory/stm/'
LTM_FOLDER = './memory/ltm/'

# Dimension of the deterministic feature vector produced from each memory.
# Must match the input_size of the SimpleMind model being trained.
INPUT_DIM = 16

class Coach:
    def __init__(self, model):
        self.model = model
        self.truth_memory_path = './memory/truth/'

    def _extract_pair(self, entry):
        """Extract (instruction, response) from one STM record, tolerating the
        two shapes written by memory/memory.py:
          - store_in_stm:            {"instruction": ..., "response": ...}
          - save_conversation_memory: {"dialog": {"instruction": ..., "response": ...}}
            (and other nested/flat variants). Returns None if neither fits.
        """
        if not isinstance(entry, dict):
            return None
        # Nested dialog shape.
        if isinstance(entry.get('dialog'), dict):
            inner = entry['dialog']
            return (str(inner.get('instruction', '')), str(inner.get('response', '')))
        # Flat shape.
        if 'instruction' in entry or 'response' in entry:
            return (str(entry.get('instruction', '')), str(entry.get('response', '')))
        return None

    def load_beliefs(self):
        """
        Load memories from the STM folder as (instruction, response) pairs.
        Preprocessed-data files (which have 'X'/'y' keys) are skipped here.
        """
        beliefs = []
        if os.path.exists(STM_FOLDER):
            for file_name in os.listdir(STM_FOLDER):
                if not file_name.endswith('.json'):
                    continue
                if file_name.startswith('preprocessed_data_'):
                    continue
                file_path = os.path.join(STM_FOLDER, file_name)
                try:
                    with open(file_path, 'r') as file:
                        entry = json.load(file)
                except (ValueError, OSError) as e:
                    logger.warning(f"Skipping unreadable STM file {file_name}: {e}")
                    continue
                pair = self._extract_pair(entry)
                if pair is not None:
                    beliefs.append(pair)
        else:
            logger.error(f"STM path {STM_FOLDER} does not exist.")
        return beliefs

    def _featurize(self, text):
        """Deterministic hashed bag-of-words feature vector of size INPUT_DIM.

        Each whitespace token is hashed into one of INPUT_DIM buckets and the
        counts are L2-normalized. Chosen because it is dependency-free, stable
        across runs (uses zlib.crc32, not the salted built-in hash), and maps
        arbitrary-length text into the network's fixed input dimension.
        """
        import zlib
        vec = [0.0] * INPUT_DIM
        for token in str(text).lower().split():
            bucket = zlib.crc32(token.encode('utf-8')) % INPUT_DIM
            vec[bucket] += 1.0
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def preprocess_beliefs(self, beliefs):
        """
        Preprocess (instruction, response) pairs into input features (X) and
        target labels (y). X is the hashed bag-of-words vector of the
        instruction. y is a deterministic supervision signal: 1.0 when the
        memory has a non-empty response, else 0.0 (a stand-in for the old
        'valid' status now that STM records carry no explicit status field).
        """
        _require_jax()
        instructions = [instr for instr, _ in beliefs]
        responses = [1.0 if resp.strip() else 0.0 for _, resp in beliefs]

        X = jnp.array([self._featurize(instr) for instr in instructions])
        y = jnp.array([[resp] for resp in responses])

        return X, y

    def save_preprocessed_data(self, X, y):
        """
        Save preprocessed data to the STM folder.
        """
        if not os.path.exists(STM_FOLDER):
            os.makedirs(STM_FOLDER)
        data = {'X': X.tolist(), 'y': y.tolist()}
        timestamp = str(int(time.time()))
        file_path = os.path.join(STM_FOLDER, f"preprocessed_data_{timestamp}.json")
        with open(file_path, 'w') as file:
            json.dump(data, file)
        logger.info(f"Saved preprocessed data to {file_path}")

    def load_preprocessed_data(self):
        """
        Load preprocessed data and return X and y.
        """
        _require_jax()
        X, y = [], []
        if os.path.exists(STM_FOLDER):
            for file_name in os.listdir(STM_FOLDER):
                # Only read preprocessed_data_*.json here, never raw memories.
                if not file_name.startswith('preprocessed_data_'):
                    continue
                file_path = os.path.join(STM_FOLDER, file_name)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    X.append(jnp.array(data['X']))
                    y.append(jnp.array(data['y']))
        else:
            logger.error(f"STM path {STM_FOLDER} does not exist.")
        return jnp.concatenate(X, axis=0), jnp.concatenate(y, axis=0)

    def save_conclusions(self, conclusions):
        """
        Save conclusions to the LTM folder.
        """
        if not os.path.exists(LTM_FOLDER):
            os.makedirs(LTM_FOLDER)
        timestamp = str(int(time.time()))
        file_path = os.path.join(LTM_FOLDER, f"conclusions_{timestamp}.json")
        with open(file_path, 'w') as file:
            json.dump(conclusions, file)
        logger.info(f"Saved conclusions to {file_path}")

    def save_model(self, model, path):
        """
        Save the trained model to the specified path.
        """
        model_params = {
            "params": {k: v.tolist() for k, v in model.params.items()},
            "optimizer_name": model.optimizer_name,
            "learning_rate": model.learning_rate,
            "regularization": model.regularization,
            "reg_lambda": model.reg_lambda
        }

        with open(path, 'wb') as f:
            pickle.dump(model_params, f)
        logger.info(f"Saved model to {path}")

    def load_model(self, path):
        """
        Load the trained model from the specified path.
        """
        with open(path, 'rb') as f:
            model_params = pickle.load(f)

        self.model.params = {k: jnp.array(v) for k, v in model_params['params'].items()}
        self.model.optimizer_name = model_params["optimizer_name"]
        self.model.learning_rate = model_params["learning_rate"]
        self.model.regularization = model_params["regularization"]
        self.model.reg_lambda = model_params["reg_lambda"]
        logger.info(f"Loaded model from {path}")

    def train_on_beliefs(self, epochs):
        """
        Train the model on beliefs.
        """
        beliefs = self.load_beliefs()
        if beliefs:
            X, y = self.preprocess_beliefs(beliefs)
            self.save_preprocessed_data(X, y)
            self.model.train(X, y, epochs)
            conclusions = {"final_output": self.model.forward(X).tolist()}
            self.save_conclusions(conclusions)
            os.makedirs('./model', exist_ok=True)
            self.save_model(self.model, './model/simple_mind.pkl')
            logger.info("Training completed.")
        else:
            logger.warning("No memories yet in ./memory/stm — nothing to train on.")

    def log_to_mindx(self, message):
        """
        Log a message to the MindX folder.
        """
        mindx_folder = './mindx/agency/'
        if not os.path.exists(mindx_folder):
            os.makedirs(mindx_folder)
        with open(os.path.join(mindx_folder, 'log.txt'), 'a') as log_file:
            log_file.write(message + '\n')

# Example usage
if __name__ == "__main__":
    # input_size must match the featurizer's INPUT_DIM.
    input_size = INPUT_DIM
    hidden_sizes = [10, 10]
    output_size = 1
    learning_rate = 0.001
    epochs = 1000

    # Constructing SimpleMind raises a helpful install hint when jax is missing.
    simple_mind = SimpleMind(input_size, hidden_sizes, output_size, activation='relu', optimizer='adam', learning_rate=learning_rate, regularization='l2', reg_lambda=0.01)
    coach = Coach(simple_mind)
    coach.train_on_beliefs(epochs)
    coach.log_to_mindx("Training session completed.")


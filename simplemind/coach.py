# coach.py (c) 2024 Gregory L. Magnusson MIT licence
# trainer for SimpleMind neural network
import os
import json
import logging
import time
import pickle
import jax.numpy as jnp
from SimpleMind import SimpleMind

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Coach')

STM_FOLDER = './memory/stm/'
LTM_FOLDER = './memory/ltm/'

class Coach:
    def __init__(self, model):
        self.model = model
        self.truth_memory_path = './memory/truth/'

    def load_beliefs(self):
        """
        Load beliefs from the STM folder.
        """
        beliefs = []
        if os.path.exists(STM_FOLDER):
            for file_name in os.listdir(STM_FOLDER):
                if file_name.endswith('.json'):
                    file_path = os.path.join(STM_FOLDER, file_name)
                    with open(file_path, 'r') as file:
                        belief = json.load(file)
                        beliefs.append(belief)
        else:
            logger.error(f"STM path {STM_FOLDER} does not exist.")
        return beliefs

    def preprocess_beliefs(self, beliefs):
        """
        Preprocess beliefs into input features (X) and target labels (y).
        """
        instructions = [belief['belief'] for belief in beliefs]
        responses = [1 if belief['status'] == 'valid' else 0 for belief in beliefs]

        # Example preprocessing: Convert strings to lengths (this can be customized)
        X = jnp.array([[len(instr)] for instr in instructions])
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
        X, y = [], []
        if os.path.exists(STM_FOLDER):
            for file_name in os.listdir(STM_FOLDER):
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
            X_train, y_train = self.load_preprocessed_data()
            self.model.train(X_train, y_train, epochs)
            conclusions = {"final_output": self.model.forward(X_train).tolist()}
            self.save_conclusions(conclusions)
            self.save_model(self.model, './model/simple_mind.pkl')
            logger.info("Training completed.")
        else:
            logger.warning("No beliefs to train on.")

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
    input_size = 4
    hidden_sizes = [10, 10]
    output_size = 1
    learning_rate = 0.001
    epochs = 1000

    X = jnp.array([[1.0, 2.0, 3.0, 4.0]])
    y = jnp.array([[1.0]])

    simple_mind = SimpleMind(input_size, hidden_sizes, output_size, activation='relu', optimizer='adam', learning_rate=learning_rate, regularization='l2', reg_lambda=0.01)
    coach = Coach(simple_mind)
    coach.train_on_beliefs(epochs)
    coach.log_to_mindx("Training session completed.")


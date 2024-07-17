# epistemic.py (c) 2024 Gregory L. Magnusson MIT license
# Epistemic Logic as an extension to BDI (Belief-Desire-Intention) model

import logging
import json
import os
from datetime import datetime
from logic import LogicTables  # Importing the LogicTables class from logic.py
from bdi import Belief, Desire, Intention, Goal, Reward  # Importing BDI classes
from chatter import GPT4o, GroqModel, OllamaModel  # Importing reasoning models
from webmind.api import APIManager  # Importing API manager
from memory.memory import create_memory_folders, store_in_stm, DialogEntry  # Importing memory management

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    handlers=[logging.FileHandler("epistemic.log"), logging.StreamHandler()]
)
logger = logging.getLogger('AutoepistemicAgent')

class AutoepistemicAgent:
    def __init__(self, initial_beliefs, default_rules):
        # Initialize beliefs and default rules
        self.beliefs = set(initial_beliefs)
        self.default_rules = default_rules
        self.logic = LogicTables()  # Initialize logic tables for reasoning
        self.belief_priority = {belief: 1 for belief in self.beliefs}  # Default priority for each belief

        # Initialize logic variables and expressions
        for belief in self.beliefs:
            self.logic.add_variable(belief)
            self.logic.add_expression(belief)

    def add_information(self, new_information):
        # Add new information to beliefs
        logger.info(f"Adding new information: {new_information}")
        self.beliefs.update(new_information)
        self.revise_beliefs()

    def revise_beliefs(self):
        # Revise beliefs based on new information
        logger.info(f"Revising beliefs with current knowledge: {self.beliefs}")
        initial_beliefs = self.beliefs.copy()
        revised = True
        while revised:
            revised = False
            for belief in list(initial_beliefs):
                if self.contradicts_new_information(belief):
                    self.beliefs.remove(belief)
                    logger.info(f"Retracting belief: {belief}")
                    revised = True
            initial_beliefs = self.beliefs.copy()
        logger.info(f"Beliefs after revision: {self.beliefs}")

    def contradicts_new_information(self, belief):
        # Check if a belief contradicts new information
        for rule in self.default_rules:
            if rule['default'] == belief and rule['contradiction'] in self.beliefs:
                return True
        return False

    def validate_belief(self, belief):
        # Validate a belief using logic tables
        return self.logic.validate_truth(belief)

    def prioritize_belief(self, belief, priority):
        # Set the priority of a belief
        if belief in self.beliefs:
            self.belief_priority[belief] = priority
            logger.info(f"Set priority of belief '{belief}' to {priority}")
        else:
            logger.warning(f"Belief '{belief}' not found to set priority")

    def save_configuration(self, filepath):
        # Save the current configuration to a file
        config = {
            'initial_beliefs': list(self.beliefs),
            'default_rules': self.default_rules,
            'belief_priority': self.belief_priority
        }
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Configuration saved to {filepath}")

    def load_configuration(self, filepath):
        # Load configuration from a file
        if not os.path.exists(filepath):
            logger.error(f"Configuration file {filepath} does not exist")
            return
        with open(filepath, 'r') as f:
            config = json.load(f)
            self.beliefs = set(config['initial_beliefs'])
            self.default_rules = config['default_rules']
            self.belief_priority = config['belief_priority']
        logger.info(f"Configuration loaded from {filepath}")

# Example default rules
default_rules = [
    {"default": "Birds can fly", "contradiction": "Penguins can't fly"},
    {"default": "Birds can fly", "contradiction": "Ostriches can't fly"},
    {"default": "It is daytime", "contradiction": "It is night"},
]

# Example usage
if __name__ == "__main__":
    initial_beliefs = {"Birds can fly", "It is daytime"}
    agent = AutoepistemicAgent(initial_beliefs, default_rules)

    # Load configuration if exists
    config_path = "epistemic_config.json"
    agent.load_configuration(config_path)

    # Add new information and revise beliefs
    new_information = {"Penguins can't fly"}
    agent.add_information(new_information)

    new_information = {"It is night"}
    agent.add_information(new_information)

    # Prioritize beliefs
    agent.prioritize_belief("Birds can fly", 2)
    agent.prioritize_belief("It is daytime", 1)

    # Save configuration
    agent.save_configuration(config_path)

    logger.info(f"Final beliefs: {agent.beliefs}")

# Epistemic Logic as an extension to BDI (Belief-Desire-Intention) model

# Basic Assumptions: Autoepistemic logic assumes that an agent has some initial beliefs or assumptions about the world.

# Default Rules: Nonmonotonic reasoning in autoepistemic logic involves the use of default rules. 
# These rules capture common-sense reasoning and are assumed to hold in the absence of contradictory evidence.

# Adding Information: When new information is added to the agent's knowledge base, it can lead to the reevaluation of previously drawn conclusions.

# Revised Beliefs: Autoepistemic logic allows the agent to revise its beliefs based on the new information while maintaining consistency with its original beliefs.

# Withdrawal of Conclusions:
# autoepistemic logic permits the withdrawal of previously drawn conclusions when they conflict with the newly acquired information.

# Reasoning Process: The agent's reasoning process involves iteratively considering default rules and their implications in light of the new information. 
# If a contradiction arises, the agent may retract conclusions that were previously drawn based on default rules.

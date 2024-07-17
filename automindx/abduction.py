# abduction.py (c) 2024 Gregory L. Magnusson MIT licence
# infers the most likely explanation for a given observation

import json
import random
import logging
from typing import List, Dict

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Proposition:
    """
    Class representing a proposition or statement.
    """
    def __init__(self, statement: str):
        self.statement = statement

    def __str__(self):
        return self.statement

class AbductiveReasoning:
    """
    Class handling the abductive reasoning process.
    """
    def __init__(self, knowledge_base: Dict):
        self.knowledge_base = knowledge_base

    def reason(self, observation: str) -> str:
        """
        Infers the most likely explanation for a given observation.
        """
        logging.info(f"Reasoning for observation: {observation}")
        possible_explanations = self.find_possible_explanations(observation)
        best_explanation = self.select_best_explanation(possible_explanations)
        return best_explanation

    def find_possible_explanations(self, observation: str) -> List[str]:
        """
        Searches the knowledge base for possible explanations of the observation.
        """
        explanations = [fact for fact in self.knowledge_base["facts"] if self.explains(observation, fact)]
        logging.info(f"Possible explanations found: {explanations}")
        return explanations

    def explains(self, observation: str, fact: str) -> bool:
        """
        Determines if a fact can explain the observation.
        """
        return fact in observation

    def select_best_explanation(self, explanations: List[str]) -> str:
        """
        Selects the best explanation from possible explanations.
        """
        if explanations:
            best_explanation = random.choice(explanations)
            logging.info(f"Selected explanation: {best_explanation}")
            return best_explanation
        logging.warning("No explanations found.")
        return "No explanation found."

class AbductionAgent:
    """
    Agent class that manages the knowledge base and uses AbductiveReasoning to handle observations.
    """
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        self.reasoner = AbductiveReasoning(self.knowledge_base)

    def load_knowledge_base(self, path: str) -> Dict:
        """
        Loads the knowledge base from a JSON file.
        """
        try:
            with open(path, 'r') as file:
                knowledge_base = json.load(file)
            logging.info(f"Knowledge base loaded from {path}")
            return knowledge_base
        except Exception as e:
            logging.error(f"Error loading knowledge base: {e}")
            return {"facts": []}

    def handle_observation(self, observation: str) -> str:
        """
        Handles an observation by using the reasoner to find the best explanation.
        """
        return self.reasoner.reason(observation)

if __name__ == "__main__":
    # Example usage
    agent = AbductionAgent("knowledge_base.json")
    observation = "The ground is wet."
    explanation = agent.handle_observation(observation)
    print(f"Observation: {observation}")
    print(f"Explanation: {explanation}")

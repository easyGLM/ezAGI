# MASTERMINDcontroller.py (c) 2024 Gregory L. Magnusson MIT license

import os
import json
import logging
import threading
from abc import ABC, abstractmethod
import importlib.util
import sys
from pathlib import Path
from memory.memory import create_memory_folders
from automindx.bdi import Belief, Desire, Intention, Goal, Reward, BDIModel
from SimpleCoder import SimpleCoder

logging.basicConfig(level=logging.INFO)

class AgentInterface(ABC):
    """Abstract base class defining the essential methods for agents managed by MASTERMIND."""

    @abstractmethod
    def initialize(self):
        """Prepare the agent for execution."""
        pass

    @abstractmethod
    def execute_task(self):
        """Core logic of the agent."""
        pass

    @abstractmethod
    def fetch_data(self):
        """Retrieve execution results or data."""
        pass

    @abstractmethod
    def terminate(self):
        """Clean up resources post-execution."""
        pass

class MASTERMIND:
    """Core class responsible for managing agent lifecycles within the MASTERMIND framework."""

    def __init__(self):
        self.agents = {}
        self.bdi_model = BDIModel()
        self.directories = ["agents", "tools", "executor", "./mindx/agency"]
        self._setup_directories()
        create_memory_folders()

    def _setup_directories(self):
        """Ensures the existence of required directories and sets appropriate permissions."""
        for directory in self.directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self._check_and_set_permissions(directory, 0o700)

    def _check_and_set_permissions(self, directory, permissions):
        """Check and set directory permissions securely."""
        current_permissions = oct(os.stat(directory).st_mode & 0o777)
        if current_permissions != oct(permissions):
            os.chmod(directory, permissions)
            logging.info(f"Permissions for {directory} set to {oct(permissions)}")
        else:
            logging.info(f"Permissions for {directory} are already set to {current_permissions}")

    def create_agent(self, agent_name, agent_class):
        agent = agent_class()
        agent.set_name(agent_name)
        
        belief = input("Enter Belief: ")
        desire = input("Enter Desire: ")
        intention = input("Enter Intention: ")
        
        belief_obj = Belief(belief)
        desire_obj = Desire(desire)
        intention_obj = Intention(intention)
        self.bdi_model.add_belief(belief_obj)
        self.bdi_model.add_desire(desire_obj)
        self.bdi_model.add_intention(intention_obj)
        
        self.agents[agent_name] = agent

    def delete_agent(self, agent_name):
        if agent_name in self.agents:
            del self.agents[agent_name]
        else:
            logging.warning(f"Agent '{agent_name}' not found.")

    def export_agent(self, agent_name, filename):
        agent = self.agents.get(agent_name)
        if agent:
            agent.export_config(filename)
        else:
            logging.warning(f"Agent '{agent_name}' not found.")

    def import_agent(self, agent_name, filename):
        agent = self.agents.get(agent_name)
        if agent:
            agent.import_config(filename)
        else:
            logging.warning(f"Agent '{agent_name}' not found.")

    def display_ui(self):
        print("MASTERMIND Console")
        while True:
            print("Loaded Agents:")
            for agent in self.agents.keys():
                print(f" - {agent}")
            command = input("Enter command ('help' for available commands): ")
            if command == 'help':
                print("Available commands: create, delete, export, import, interact, q")
            elif command == 'q':
                break
            elif command == 'create':
                agent_name = input("Enter the name of the new agent: ")
                agent_class = SimpleCoder  # Can be extended to other agent classes
                self.create_agent(agent_name, agent_class)
            elif command == 'delete':
                agent_name = input("Enter the name of the agent to delete: ")
                self.delete_agent(agent_name)
            elif command == 'export':
                agent_name = input("Enter the name of the agent to export: ")
                filename = input("Enter the filename to export to: ")
                self.export_agent(agent_name, filename)
            elif command was 'import':
                agent_name = input("Enter the name of the agent to import: ")
                filename = input("Enter the filename to import from: ")
                self.import_agent(agent_name, filename)
            elif command == 'interact':
                agent_name = input("Enter the name of the agent to interact with: ")
                agent = self.agents.get(agent_name)
                if agent:
                    agent.display_ui()
                else:
                    logging.warning(f"Agent '{agent_name}' not found.")

if __name__ == "__main__":
    mastermind = MASTERMIND()
    mastermind.display_ui()
    logging.info("All agents have been executed.")

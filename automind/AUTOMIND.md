
# AUTOMIND.md
Overview

The automind folder within the easyAGI project contains essential components that enable advanced reasoning, decision-making, and logic processing for the AGI system. Below is a detailed description of the three primary files in this directory: SocraticReasoning.py, agi.py, and logic.py.

# SocraticReasoning.py

Purpose:
The SocraticReasoning.py module implements a Socratic reasoning engine that interacts with a chatter model to add, challenge, and draw conclusions from premises. It aims to simulate a logical reasoning process, allowing the AGI to engage in structured dialogues and make informed decisions based on logical premises.

Key Features:

    Initialization: Sets up logging, defines file paths for saving premises, non-premises, conclusions, and truth tables, and ensures necessary directories exist.
    Premise Management: Provides methods to add, validate, and remove premises. Stores valid premises and logs invalid ones.
    Conclusion Drawing: Attempts to draw conclusions based on the current set of premises and validates these conclusions using logic tables.
    Logging: Implements detailed logging mechanisms for general operations and specific errors.
    Interactive Loop: Includes an interactive loop for user commands to add, challenge premises, and draw conclusions.

# agi.py

Purpose:
The agi.py file defines the AGI (Artificial General Intelligence) class, which uses Socratic reasoning to learn from data and make decisions. This file integrates various components such as the chatter model and memory management to facilitate the AGI's decision-making processes.

Key Features:

    AGI Class: Initializes with a chatter instance and Socratic reasoning. Provides methods to learn from data and make decisions based on propositions.
    EasyAGI Class: Manages API keys, initializes the AGI, and handles memory initialization. Contains the main loop to interact with the environment and make decisions.
    Main Loop: Continuously interacts with the environment, processes input data, learns from it, and makes decisions. Logs and stores dialog entries in memory.
    Logging: Includes basic logging setup and ensures proper logging of decisions and interactions.

# logic.py

Purpose:
The logic.py module provides the LogicTables class, which manages logical variables, expressions, and truth tables. It evaluates logical expressions and ensures their validity, supporting the reasoning processes of the AGI.

Key Features:

    Initialization: Sets up logging and ensures directories for logs exist.
    Variable and Expression Management: Methods to add variables and expressions while ensuring they are not duplicated.
    Truth Table Generation: Generates and displays truth tables for the current set of variables and expressions.
    Evaluation and Validation: Evaluates logical expressions and validates them as truths or tautologies.
    Logging: Implements detailed logging for all operations and stores logs in both general and memory-specific files.
    Output Methods: Outputs beliefs and truths to JSON files, ensuring structured storage of logical data.


For each of these modules, an example usage is provided to demonstrate how the classes and methods can be utilized within the easyAGI project. These examples help in understanding the practical applications of the classes and their methods.

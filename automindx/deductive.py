# deductive.py
# deductive (c) 2024 Trung Luong MIT licence
# deductive (c) 2024 Gregory L. Magnusson MIT licence

from collections import defaultdict
import datetime
import json
import logging
import pathlib
from logic import LogicTables, save_valid_truth

class Graph:
    """
    Create graph for condition statements
    Ex: A -> B
    """

    def __init__(self):
        self.graph = defaultdict(list)

    def add_condition_statement(self, arg1, arg2):
        """
        Add a condition statement to the graph.
        """
        self.graph[arg1].append(arg2)

    def print_graph(self):
        """
        Print the graph.
        """
        for k, v in self.graph.items():
            print(k)
            for i in v:
                print(' |-> ' + i)
            print('\n')

    def get_graph(self):
        """
        Get the graph.
        """
        return self.graph

class Node:
    """
    Class to represent a node in the graph.
    """
    def __init__(self, value):
        self.value = value
        self.parent = None

def law_of_syllogism(graph, start, dest):
    """
    Law of syllogism

    1. P -> Q
    2. Q -> R
    3. Therefore: P -> R

    Using Breadth First Search algorithm to perform Law of syllogism.
    """

    queue = []
    tree = {}

    # Flag to check if there is a path from start to dest
    flag = None

    # List for vertices visited
    visited = []

    # Create BFS tree
    tree[start] = Node(start)

    # Mark the start node as visited and enqueue it
    queue.append(start)
    visited.append(start)

    while queue:
        # Dequeue a vertex from queue
        s = queue.pop(0)

        # Get all adjacent vertices of the dequeue vertex s.
        # If an adjacent has not been visited, then mark it visited and enqueue it
        for i in graph[s]:
            if i not in visited:
                queue.append(i)
                visited.append(i)
                # Add adjacent to Tree BFS
                tree[i] = Node(i)
                tree[i].parent = tree[s]

    # Check the path to destination
    if dest not in tree.keys():
        flag = False
    else:
        flag = True

    return flag

def modus_ponens(graph, arg1, arg2, antecedent_list):
    """
    Modus ponens

    1. arg1 -> arg2 (First premise is a conditional statement)
    2. arg1 (Second premise is the antecedent)
    3. arg2 (Conclusion deduced is the consequent)
    """

    # String for first and second premise
    premise = '1. ' + arg1 + ' -> ' + arg2 + '\n' + '2. ' + arg1 + '\n' + '-' * 20 + '\n' + '3. '

    if not law_of_syllogism(graph, arg1, arg2):
        return "Don't exist the conclusion"
    else:
        if arg1 not in antecedent_list:
            return "Don't exist the conclusion"
        else:
            return premise + arg2

def modus_tollens(graph, arg1, arg2, negative_consequent_list):
    """
    Modus tollens

    1. arg1 -> arg2 (First premise is a conditional statement)
    2. ¬arg2 (Second premise is the negation of the consequent)
    3. ¬arg1 (Conclusion deduced is the negation of the antecedent)
    """

    # String for first and second premise
    premise = '1. ' + arg1 + ' -> ' + arg2 + '\n' + '2. ¬' + arg2 + '\n' + '-' * 20 + '\n' + '3. '

    if not law_of_syllogism(graph, arg1, arg2):
        return "Don't exist the conclusion"
    else:
        if arg2 not in negative_consequent_list:
            return "Don't exist the conclusion"
        else:
            return premise + '¬' + arg1

def unify(var, term, substitution):
    """
    Unify a variable with a term.
    """
    if var == term:
        return substitution
    elif var in substitution:
        return unify(substitution[var], term, substitution)
    elif isinstance(term, str) and term in substitution:
        return unify(var, substitution[term], substitution)
    else:
        substitution[var] = term
        return substitution

def unify_expressions(expr1, expr2, substitution):
    """
    Unify two expressions.
    """
    if expr1 == expr2:
        return substitution
    elif isinstance(expr1, str) and expr1.islower():
        return unify(expr1, expr2, substitution)
    elif isinstance(expr2, str) and expr2.islower():
        return unify(expr2, expr1, substitution)
    elif isinstance(expr1, list) and isinstance(expr2, list) and len(expr1) == len(expr2):
        for e1, e2 in zip(expr1, expr2):
            substitution = unify_expressions(e1, e2, substitution)
        return substitution
    else:
        return None

# Integration with logic.py for logging and memory management
def log_belief(belief):
    belief_path = './memory/truth'
    pathlib.Path(belief_path).mkdir(parents=True, exist_ok=True)
    belief_file = f"{belief_path}/{datetime.datetime.now().isoformat()}_belief.json"
    with open(belief_file, 'w') as file:
        json.dump({"belief": belief, "timestamp": datetime.datetime.now().isoformat()}, file)

def log_fact(fact):
    fact_path = './memory/truth'
    pathlib.Path(fact_path).mkdir(parents=True, exist_ok=True)
    fact_file = f"{fact_path}/{datetime.datetime.now().isoformat()}_fact.json"
    with open(fact_file, 'w') as file:
        json.dump({"fact": fact, "timestamp": datetime.datetime.now().isoformat()}, file)

def log_contingent(contingent_data):
    contingent_path = './memory/truth'
    pathlib.Path(contingent_path).mkdir(parents=True, exist_ok=True)
    contingent_file = f"{contingent_path}/{contingent_data['timestamp']}_contingent.json"
    with open(contingent_file, 'w') as file:
        json.dump(contingent_data, file)

def log_truth(truth_data):
    truth_path = './memory/truth'
    pathlib.Path(truth_path).mkdir(parents=True, exist_ok=True)
    truth_file = f"{truth_path}/{truth_data['timestamp']}_truth.json"
    with open(truth_file, 'w') as file:
        json.dump(truth_data, file)

# Example usage
if __name__ == '__main__':
    g = Graph()
    g.add_condition_statement('P', 'Q')
    g.add_condition_statement('Q', 'R')

    # Create list of antecedents
    ant_list = ['P', 'Q']

    # Create list of the negation of the consequents
    cons_list = ['Q', 'R']

    # Deductive Reasoning
    conclusion1 = modus_ponens(g.get_graph(), 'P', 'R', ant_list)
    log_belief(conclusion1)
    print(conclusion1)

    print('\n\n')

    conclusion2 = modus_ponens(g.get_graph(), 'P', 'K', ant_list)
    log_belief(conclusion2)
    print(conclusion2)

    print('\n\n')

    conclusion3 = modus_tollens(g.get_graph(), 'P', 'Q', cons_list)
    log_belief(conclusion3)
    print(conclusion3)

    print('\n\n')

    conclusion4 = modus_tollens(g.get_graph(), 'P', 'A', cons_list)
    log_belief(conclusion4)
    print(conclusion4)
    
    # Unification examples
    substitution = {}
    unified_substitution = unify_expressions(['f', 'x', 'y'], ['f', 'a', 'b'], substitution)
    print("Unification result:", unified_substitution)

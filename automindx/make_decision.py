# make_decision.py (c) 2024 Gregory L. Magnusson
# from draw_conclusion boolean controls make_decision autonomous challenge of SocraticReasoning conclusion
import logging
import os
import pathlib
import ujson
from datetime import datetime
import itertools
from epistemic import AutoepistemicAgent  # Importing AutoepistemicAgent from epistemic.py
from fuzzy import FuzzyLogic  # Importing FuzzyLogic from fuzzy.py
from nonmonotonic import NonmonotonicReasoning  # Importing NonmonotonicReasoning from nonmonotonic.py
from bdi import Belief, Desire, Intention, Goal, Reward  # Importing BDI classes
from webmind.chatter import GPT4o, GroqModel, OllamaModel
from webmind.api import APIManager

# Proposition class to handle logical statements
class Proposition:
    def __init__(self, statement):
        self.statement = statement

    def __str__(self):
        return self.statement

class Reasoning:
    def __init__(self):
        self.epistemic_agent = AutoepistemicAgent([], [])  # Initialize with empty beliefs and rules
        self.fuzzy_logic = FuzzyLogic()
        self.nonmonotonic_reasoning = NonmonotonicReasoning()

    def epistemic_reasoning(self, new_information):
        self.epistemic_agent.add_information(new_information)
        self.epistemic_agent.revise_beliefs()
        return self.epistemic_agent.beliefs

    def fuzzy_reasoning(self, variables, rules):
        return self.fuzzy_logic.evaluate(variables, rules)

    def nonmonotonic_reasoning(self, premises):
        return self.nonmonotonic_reasoning.reason(premises)

# LogicTables class for managing logical variables, expressions, and truth tables
class LogicTables:
    def __init__(self):
        self.variables = []
        self.expressions = []
        self.valid_truths = []
        self.logger = logging.getLogger('LogicTables')
        self.logger.setLevel(logging.DEBUG)

        # Ensure directories exist
        general_log_dir = './mindx/decisions/'
        memory_log_dir = './mindx/decisions/'
        pathlib.Path(general_log_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(memory_log_dir).mkdir(parents=True, exist_ok=True)

        # General log file for mindx
        file_handler_mindx = logging.FileHandler(f'{general_log_dir}/decisionlog.txt')
        file_handler_mindx.setLevel(logging.DEBUG)
        file_formatter_mindx = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler_mindx.setFormatter(file_formatter_mindx)

        # Log file for memory/decisions
        file_handler_memory = logging.FileHandler(f'{memory_log_dir}/decisionlog.txt')
        file_handler_memory.setLevel(logging.DEBUG)
        file_formatter_memory = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler_memory.setFormatter(file_formatter_memory)

        self.logger.addHandler(file_handler_mindx)
        self.logger.addHandler(file_handler_memory)

        # Remove any other handlers (like StreamHandler) if they exist
        self.logger.propagate = False

    def log(self, message, level='info'):
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        self.store_log_in_mindx(message, level)
        self.store_log_in_memory(message, level)

    def store_log_in_mindx(self, message, level):
        general_log_path = './mindx/decisions/decisionlog.txt'
        pathlib.Path(general_log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(general_log_path, 'a') as file:
            file.write(f"{level.upper()}: {message}\n")

    def store_log_in_memory(self, message, level):
        memory_log_path = './mindx/decisions/decisionlog.txt'
        pathlib.Path(memory_log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(memory_log_path, 'a') as file:
            file.write(f"{level.upper()}: {message}\n")

    def add_variable(self, var):
        if var not in self.variables:
            self.variables.append(var)
            self.log(f"Added variable: {var}")
            self.output_belief(f"Added variable: {var}")
        else:
            self.log(f"Variable {var} already exists.", level='warning')

    def add_expression(self, expr):
        if expr not in self.expressions:
            self.expressions.append(expr)
            self.log(f"Added expression: {expr}")
            self.output_belief(f"Added expression: {expr}")
        else:
            self.log(f"Expression {expr} already exists.", level='warning')

    def output_belief(self, belief):
        belief_path = './mindx/decisions/'
        pathlib.Path(belief_path).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        belief_data = {"belief": belief, "timestamp": timestamp}
        belief_file = f"{belief_path}/{timestamp}_belief.json"
        with open(belief_file, 'w') as file:
            ujson.dump(belief_data, file)
        self.log(f"Stored belief: {belief_data}", level='info')

    def output_truth(self, variables, expressions, truth_table):
        truth_path = './mindx/decisions/'
        pathlib.Path(truth_path).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        truth_data = {
            "belief": {
                "variables": variables,
                "expressions": expressions,
                "truth_table": truth_table
            },
            "timestamp": timestamp
        }
        truth_file = f"{truth_path}/{timestamp}_truth.json"
        with open(truth_file, 'w') as file:
            ujson.dump(truth_data, file)
        self.log(f"Stored truth: {truth_data}", level='info')

    def evaluate_expression(self, expr, values):
        allowed_operators = {
            'and': lambda x, y: x and y,
            'or': lambda x, y: x or y,
            'not': lambda x: not x,
            'xor': lambda x, y: x ^ y,
            'nand': lambda x, y: not (x and y),
            'nor': lambda x, y: not (x or y),
            'implication': lambda x, y: not x or y
        }
        try:
            result = eval(expr, {"__builtins__": None}, {**allowed_operators, **values})
            self.log(f"Evaluated expression '{expr}' with values {values}: {result}")
            return result
        except Exception as e:
            self.log(f"Error evaluating expression '{expr}': {e}", level='error')
            return False

    def generate_truth_table(self):
        n = len(self.variables)
        combinations = list(itertools.product([True, False], repeat=n))
        truth_table = []
        for combo in combinations:
            values = {self.variables[i]: combo[i] for i in range(n)}
            result = values.copy()
            for expr in self.expressions:
                result[expr] = self.evaluate_expression(expr, values)
            truth_table.append(result)
        self.log(f"Generated truth table with {len(truth_table)} rows")
        self.output_belief(f"Generated truth table with {len(truth_table)} rows")
        self.output_truth(self.variables, self.expressions, truth_table)
        return truth_table

    def display_truth_table(self):
        truth_table = self.generate_truth_table()
        headers = self.variables + self.expressions
        print("\t".join(headers))
        for row in truth_table:
            print("\t".join(str(row[var]) for var in headers))

    def validate_truth(self, expression):
        if expression not in self.expressions:
            self.log(f"Expression '{expression}' is not in the list of expressions.", level='warning')
            return False
        truth_table = self.generate_truth_table()
        for row in truth_table:
            if not row[expression]:
                self.log(f"Expression '{expression}' is not valid.")
                return False
        self.log(f"Expression '{expression}' is valid.")
        self.save_valid_truth(expression)
        return True

    def save_valid_truth(self, expression):
        timestamp = datetime.now().isoformat()
        valid_truth = {"expression": expression, "timestamp": timestamp}
        self.valid_truths.append(valid_truth)
        self.output_truth(self.variables, self.expressions, valid_truth)
        self.log(f"Saved valid truth: '{expression}' at {timestamp}")

    def get_valid_truths(self):
        self.log("Retrieving valid truths.")
        return self.valid_truths

    def tautology(self, expression):
        truth_table = self.generate_truth_table()
        for row in truth_table:
            if not self.evaluate_expression(expression, row):
                self.log(f"Expression '{expression}' is not a tautology.", level='info')
                return False
        self.log(f"Expression '{expression}' is a tautology.", level='info')
        return True

    def modus_ponens(self, fact, rule):
        try:
            if not isinstance(fact, dict) or not isinstance(rule, dict):
                raise TypeError("Both fact and rule must be dictionaries.")
            required_keys = {'type', 'relation', 'arguments'}
            if not required_keys.issubset(fact) or not required_keys.issubset(rule):
                raise KeyError("Both fact and rule must contain the keys: 'type', 'relation', and 'arguments'.")
            if fact['type'] == 'fact' and rule['type'] == 'rule':
                if self.unify_variables(fact, rule):
                    conclusion = {
                        'type': 'fact', 
                        'relation': rule['relation'][1:], 
                        'arguments': fact['arguments']
                    }
                    self.log(f"Derived fact: {conclusion} using modus ponens.")
                    self.output_fact(conclusion, fact, rule)
                    return conclusion
        except Exception as e:
            self.log(f"Error in modus_ponens: {e}", level='error')
        return None

    def unify_variables(self, fact, rule):
        try:
            required_keys = {'relation', 'arguments'}
            if not required_keys.issubset(fact) or not required_keys.issubset(rule):
                raise KeyError("Both fact and rule must contain the keys: 'relation' and 'arguments'.")
            fact_arguments = set(fact['arguments'])
            rule_relation = set(rule['relation'])
            rule_arguments = set(rule['arguments'])
            if fact_arguments.intersection(rule_relation) or rule_arguments.intersection(set(fact['relation'])):
                return False
            return True
        except Exception as e:
            self.log(f"Error in unify_variables: {e}", level='error')
            return False

    def output_fact(self, fact, original_fact, original_rule):
        fact_path = './mindx/decisions/'
        pathlib.Path(fact_path).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        fact_file = f"{fact_path}/{timestamp}_fact.json"
        fact_data = {
            "fact": fact,
            "original_fact": original_fact,
            "original_rule": original_rule,
            "fact_arguments": list(set(original_fact['arguments'])),
            "rule_relation": list(set(original_rule['relation'])),
            "rule_arguments": list(set(original_rule['arguments'])),
            "timestamp": timestamp
        }
        with open(fact_file, 'w') as file:
            ujson.dump(fact_data, file, indent=4)
        self.log(f"Stored derived fact: {fact_data}", level='info')

# SocraticReasoning class for managing premises, conclusions, and decision making
class SocraticReasoning:
    def __init__(self, chatter):
        self.premises = []
        self.logger = logging.getLogger('SocraticReasoning')
        self.logger.setLevel(logging.DEBUG)
        logs_dir = './mindx/decisions/'
        os.makedirs(logs_dir, exist_ok=True)
        self.socraticlogs_file = './mindx/decisions/socraticdecisionlogs.txt'
        file_handler = logging.FileHandler(self.socraticlogs_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levellevelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.CRITICAL)
        stream_formatter = logging.Formatter('%(message)s')
        stream_handler.setFormatter(stream_formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        self.premises_file = './mindx/decisions/premises.json'
        self.not_premises_file = './mindx/decisions/notpremise.json'
        self.conclusions_file = './mindx/decisions/conclusions.txt'
        self.truth_tables_file = './mindx/decisions/truth.json'
        self.decisions_dir = './mindx/decisions'
        self.max_tokens = 100
        self.max_premises = 5
        self.limit_premises = False
        self.chatter = chatter
        self.logic_tables = LogicTables()
        self.dialogue_history = []
        self.logical_conclusion = ""
        create_memory_folders()

    def socraticlogs(self, message, level='info'):
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        self.log_errors(message, level)

    def log_errors(self, message, level):
        error_logs_path = './mindx/decisions/errorlogs.txt'
        pathlib.Path(error_logs_path).parent.mkdir(parents=True, exist_ok=True)
        with open(error_logs_path, 'a') as file:
            file.write(f"{level.upper()}: {message}\n")

    def log_not_premise(self, message, level='info'):
        not_premises_path = self.not_premises_file
        pathlib.Path(not_premises_path).parent.mkdir(parents=True, exist_ok=True)
        entry = {"level": level.upper(), "message": message}
        try:
            with open(not_premises_path, 'r') as file:
                logs = ujson.load(file)
        except (FileNotFoundError, ValueError):
            logs = []
        logs.append(entry)
        with open(not_premises_path, 'w') as file:
            ujson.dump(logs, file, indent=2)

    def save_premises(self):
        pathlib.Path(self.premises_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.premises_file, 'w') as file:
            ujson.dump(self.premises, file, indent=2)

    def add_premise(self, premise):
        if self.parse_statement(premise):
            self.premises.append(premise)
            self.save_premises()
        else:
            self.log_not_premise(f'Invalid premise: {premise}', level='error')

    def parse_statement(self, statement):
        return isinstance(statement, str) and len(statement) > 0

    def generate_new_premise(self, premise):
        premise_text = f"- {premise}"
        new_premise = self.chatter.generate_response(premise_text)
        return new_premise.strip()

    def challenge_premise(self, premise):
        if premise in self.premises:
            self.premises.remove(premise)
            self.socraticlogs(f'Challenged and removed premise: {premise}')
            self.remove_equivalent_premises(premise)
            self.save_premises()
        else:
            self.log_not_premise(f'Premise not found: {premise}', level='error')

    def remove_equivalent_premises(self, premise):
        equivalent_premises = [p for p in self.premises if self.logic_tables.unify_variables(premise, p)]
        for p in equivalent_premises:
            self.premises.remove(p)
            self.log_not_premise(f'Removed equivalent premise: {p}')
        self.save_premises()

    def generate_premises_and_conclusion(self, enable_additional_premises=True):
        current_premise = self.premises[0]
        additional_premises_count = 0
        while enable_additional_premises and (not self.limit_premises or additional_premises_count < self.max_premises):
            new_premise = self.generate_new_premise(current_premise)
            if not self.parse_statement(new_premise):
                continue
            self.premises.append(new_premise)
            self.save_premises()
            additional_premises_count += 1
            raw_response = self.chatter.generate_response(current_premise)
            conclusion = raw_response.strip()
            self.logical_conclusion = conclusion
            for premise in self.premises:
                fact = {"type": "fact", "relation": [premise], "arguments": []}
                rule = {"type": "rule", "relation": ["if", premise], "arguments": []}
                inferred_fact = self.logic_tables.modus_ponens(fact, rule)
                if inferred_fact and inferred_fact['relation'][0] == self.logical_conclusion:
                    self.socraticlogs(f"Inferred conclusion using modus ponens: {self.logical_conclusion}")
                    return self.logical_conclusion
            if self.validate_conclusion():
                break
            else:
                self.log_not_premise('Invalid conclusion. Generating more premises.', level='error')
        return self.logical_conclusion

    def draw_conclusion(self, enable_additional_premises=True):
        if not self.premises:
            return "No premises available for logic as conclusion."
        conclusion = self.generate_premises_and_conclusion(enable_additional_premises)
        conclusion_entry = {"premises": self.premises, "conclusion": self.logical_conclusion}
        pathlib.Path(self.premises_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.premises_file, 'w') as file:
            ujson.dump(conclusion_entry, file, indent=2)
        pathlib.Path(self.conclusions_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.conclusions_file, 'a') as file:
            file.write(f"Premises: {self.premises}\nConclusion: {self.logical_conclusion}\n")
        self.save_truth(self.logical_conclusion)
        self.premises = []
        return self.logical_conclusion

    def validate_conclusion(self):
        is_tautology = self.logic_tables.tautology(self.logical_conclusion)
        for premise in self.premises:
            fact = {"type": "fact", "relation": [premise], "arguments": []}
            rule = {"type": "rule", "relation": ["if", premise], "arguments": []}
            conclusion = self.logic_tables.modus_ponens(fact, rule)
            if conclusion and conclusion['relation'][0] == self.logical_conclusion:
                return True
        return is_tautology

    def save_truth(self, truth):
        truth_tables_entry = {
            "truth": truth,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        pathlib.Path(self.truth_tables_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.truth_tables_file, 'a') as file:
            ujson.dump(truth_tables_entry, file, indent=2)
            file.write("\n")
        self.logger.info("Saved truth: %s", truth_tables_entry)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        belief_timestamp_file = f'./mindx/decisions/belief_{timestamp}.json'
        structured_truth = {
            "truth": truth,
            "variables": self.logic_tables.variables,
            "expressions": self.logic_tables.expressions,
            "valid_truths": self.logic_tables.valid_truths,
            "timestamp": timestamp
        }
        pathlib.Path(belief_timestamp_file).parent.mkdir(parents=True, exist_ok=True)
        with open(belief_timestamp_file, 'w') as file:
            ujson.dump(structured_truth, file, indent=2)
            file.write("\n")
        self.logger.info("Saved belief with structured truth: %s", structured_truth)

    def make_decision(self, enable_additional_premises=True, autonomous=True):
        """
        Make a decision based on the logical conclusion of reasoned facts from the truth tables.
        
        Args:
            enable_additional_premises (bool): Whether to enable the generation of additional premises.
            autonomous (bool): Whether the decision-making process should be autonomous.
        
        Returns:
            str: The decision derived from the logical reasoning process.
        """
        if not self.premises:
            return "No premises available to make a decision."

        conclusion = self.generate_premises_and_conclusion(enable_additional_premises)

        while True:
            if self.validate_conclusion():
                decision = self.logical_conclusion
            else:
                # Additional logic and reasoning methods if initial validation fails
                additional_premises = self.generate_additional_premises(self.max_premises)
                for premise in additional_premises:
                    self.premises.append(premise)
                    conclusion = self.generate_premises_and_conclusion(enable_additional_premises)
                    if self.validate_conclusion():
                        decision = self.logical_conclusion
                        break
                else:
                    self.socraticlogs('Failed to validate the conclusion using existing and additional premises.', level='error')
                    decision = "Unable to make a decision based on the current premises."

            if autonomous:
                # Autonomous challenge of decision
                if not self.validate_conclusion():
                    new_premise = self.generate_new_premise(self.logical_conclusion)
                    self.add_premise(new_premise)
                else:
                    break
            else:
                break

        self.socraticlogs(f"Decision made: {decision}", level='info')

        # Save the decision along with the conclusion and premises
        decision_entry = {"premises": self.premises, "conclusion": self.logical_conclusion, "decision": decision}
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        decision_file = f'{self.decisions_dir}/decision_{timestamp}.json'
        structured_decision = {
            "decision": decision,
            "variables": self.logic_tables.variables,
            "expressions": self.logic_tables.expressions,
            "valid_truths": self.logic_tables.valid_truths,
            "timestamp": timestamp
        }
        pathlib.Path(decision_file).parent.mkdir(parents=True, exist_ok=True)
        with open(decision_file, 'w') as file:
            ujson.dump(structured_decision, file, indent=2)

        return decision

    def generate_additional_premises(self, max_premises):
        """
        Generate additional premises based on existing premises and reasoning methods.

        Args:
            max_premises (int): The maximum number of additional premises to generate.

        Returns:
            list: A list of additional premises.
        """
        additional_premises = []
        for _ in range(max_premises):
            new_premise = self.generate_new_premise(self.premises[-1])
            if self.parse_statement(new_premise):
                additional_premises.append(new_premise)
        return additional_premises

    def interact(self):
        while True:
            self.socraticlogs("\nCommands: add, challenge, conclude, set_tokens, set_premises, set_limit, toggle_limit, exit")
            cmd = input("> ").strip().lower()
            if cmd == 'exit':
                self.socraticlogs('Exiting Socratic Reasoning.')
                break
            elif cmd == 'add':
                premise = input("Enter the premise: ").strip()
                self.add_premise(premise)
            elif cmd == 'challenge':
                premise = input("Enter the premise to challenge: ").strip()
                self.challenge_premise(premise)
            elif cmd == 'conclude':
                conclusion = self.draw_conclusion(enable_additional_premises=True)
                print(conclusion)
            elif cmd == 'set_tokens':
                tokens = input("Enter the maximum number of tokens for the conclusion: ").strip()
                if tokens.isdigit():
                    self.set_max_tokens(int(tokens))
                else:
                    self.socraticlogs("Invalid number of tokens.", level='error')
                    self.log_not_premise("Invalid number of tokens.", level='error')
            elif cmd == 'set_premises':
                premises = input("Enter the maximum number of premises to generate: ").strip()
                if premises.isdigit():
                    self.set_max_premises(int(premises))
                else:
                    self.socraticlogs("Invalid number of premises.", level='error')
                    self.log_not_premise("Invalid number of premises.", level='error')
            elif cmd == 'set_limit':
                max_premises = input("Enter the maximum number of premises: ").strip()
                if max_premises.isdigit():
                    self.set_max_premises(int(max_premises))
                else:
                    self.socraticlogs("Invalid number of premises.", level='error')
                    self.log_not_premise("Invalid number of premises.", level='error')
            elif cmd == 'toggle_limit':
                self.toggle_premise_limit()
            else:
                self.log_not_premise('Invalid command.', level='error')

    def set_max_premises(self, max_premises):
        self.max_premises = max_premises
        self.socraticlogs(f"Set maximum premises to {max_premises}")

    def toggle_premise_limit(self):
        self.limit_premises = not self.limit_premises
        status = "on" if self.limit_premises else "off"
        self.socraticlogs(f"Premise limit turned {status}")

# THOT class to manage various reasoning strategies
class THOT:
    def __init__(self, reasoners, chatter):
        self.reasoners = reasoners
        self.chatter = chatter
        self.socratic_reasoner = SocraticReasoning(self.chatter)
        self.thot_log_path = './mindx/decisions/thots.json'
        self.initialize_thot_log()

    def initialize_thot_log(self):
        if not os.path.exists('./mindx'):
            os.makedirs('./mindx')
        if not os.path.exists(self.thot_log_path):
            with open(self.thot_log_path, 'w') as file:
                ujson.dump([], file)

    def log_thot(self, thot_data):
        with open(self.thot_log_path, 'r') as file:
            thots = ujson.load(file)
        thots.append(thot_data)
        with open(self.thot_log_path, 'w') as file:
            ujson.dump(thots, file, indent=4)

    def combine_results(self, proposition_p, proposition_q):
        combined_results = []
        for reasoner in self.reasoners:
            try:
                if reasoner == NonmonotonicReasoning:
                    result = reasoner.reason([proposition_p, proposition_q])
                else:
                    result = reasoner.reason(proposition_p, proposition_q)
                combined_results.append(result)
            except Exception as e:
                logging.error(f"Error in {reasoner.__name__}: {e}")
        return combined_results

    def make_decision(self, combined_results):
        decision = self.chatter.generate_response("\n".join(combined_results))
        return decision

    def refine_decision(self, decision):
        self.socratic_reasoner.add_premise(decision)
        refined_decision = self.socratic_reasoner.draw_conclusion()
        return refined_decision

# Memory folder creation function
def create_memory_folders():
    folders = [
        './mindx/decisions',
    ]
    for folder in folders:
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Actual Chatter model instantiation
    api_manager = APIManager()
    openai_key = api_manager.get_api_key('openai')
    groq_key = api_manager.get_api_key('groq')
    ollama = api_manager.get_api_key('ollama')

    if openai_key:
        chatter = GPT4o(openai_key)
    elif groq_key:
        chatter = GroqModel(groq_key)
    elif ollama:
        chatter = OllamaModel()
    else:
        raise ValueError("No valid API key found for chatter model")

    socratic_reasoning = SocraticReasoning(chatter)
    
    # Example premises
    statements = [
        "All humans are mortal.",
        "Socrates is a human."
    ]

    for statement in statements:
        socratic_reasoning.add_premise(statement)
    
    decision = socratic_reasoning.make_decision(enable_additional_premises=True, autonomous=True)
    print(f"Decision: {decision}")
    socratic_reasoning.interact()

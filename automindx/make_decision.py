# make_decision.py (c) 2024 Gregory L. Magnusson
# from draw_conclusion boolean controls make_decision autonomous challenge of SocraticReasoning conclusion
# decision orchestration on top of the canonical reasoning stack:
#   LogicTables and SocraticReasoning from automind, THOT from automindx.reasoning
import logging
import pathlib
import ujson
from datetime import datetime

from automind.logic import LogicTables
from automind.SocraticReasoning import SocraticReasoning
from automindx.reasoning import THOT
from automindx.bdi import Belief, Desire, Intention, Goal, Reward  # Importing BDI classes
from webmind.chatter import GPT4o, GroqModel, OllamaModel
from webmind.api import APIManager


# DecisionMaker extends the canonical SocraticReasoning with autonomous
# decision making, additional-premise generation and decision logging
class DecisionMaker(SocraticReasoning):
    def __init__(self, chatter):
        super().__init__(chatter)
        self.max_premises = 5  # Default maximum number of additional premises to generate
        self.limit_premises = False  # Toggle to cap additional premise generation
        self.decisions_dir = './mindx/decisions'
        pathlib.Path(self.decisions_dir).mkdir(parents=True, exist_ok=True)

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

        # Save the decision along with the conclusion and premises to ./mindx/decisions/
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        decision_file = f'{self.decisions_dir}/decision_{timestamp}.json'
        structured_decision = {
            "decision": decision,
            "premises": self.premises,
            "conclusion": self.logical_conclusion,
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

    def set_max_premises(self, max_premises):
        self.max_premises = max_premises
        self.socraticlogs(f"Set maximum premises to {max_premises}")

    def toggle_premise_limit(self):
        self.limit_premises = not self.limit_premises
        status = "on" if self.limit_premises else "off"
        self.socraticlogs(f"Premise limit turned {status}")

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
                conclusion = self.draw_conclusion()
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

    decision_maker = DecisionMaker(chatter)

    # Example premises
    statements = [
        "All humans are mortal.",
        "Socrates is a human."
    ]

    for statement in statements:
        decision_maker.add_premise(statement)

    decision = decision_maker.make_decision(enable_additional_premises=True, autonomous=True)
    print(f"Decision: {decision}")

    # tapestry of thought across every reasoning style
    thot = THOT(chatter)
    thots = thot.think(decision)
    for style, result in thots.items():
        print(f"{style}: {result}")

    decision_maker.interact()

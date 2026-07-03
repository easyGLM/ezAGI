# reasoning.py (c) Gregory L. Magnusson
# a philosphical disertation in python

import json
import logging
import os

from automind.SocraticReasoning import SocraticReasoning

class Proposition:
    def __init__(self, statement):
        self.statement = statement

    def __str__(self):
        return self.statement


class DeductiveReasoning:
    @staticmethod
    def reason(p, q):
        """
        Deductive reasoning: Draws specific conclusions from general premises.
        """
        conclusion = Proposition(f"Therefore, {q.statement.split(' ')[1]} is {p.statement.split(' ')[-1]}.")
        return f"Deductive Reasoning:\n{p}\n{q}\n{conclusion}\n"


class InductiveReasoning:
    @staticmethod
    def reason(observations):
        """
        Inductive reasoning: Forms general conclusions from specific observations.
        """
        conclusion = Proposition("Therefore, all X are Y.")
        observations_str = '\n'.join(str(obs) for obs in observations)
        return f"Inductive Reasoning:\n{observations_str}\n{conclusion}\n"


class AbductiveReasoning:
    @staticmethod
    def reason(p, q):
        """
        Abductive reasoning: Infers the most likely explanation.
        """
        conclusion = Proposition("Therefore, Y caused X.")
        return f"Abductive Reasoning:\n{p}\n{q}\n{conclusion}\n"


class AnalogicalReasoning:
    @staticmethod
    def reason(p, q):
        """
        Analogical reasoning: Draws conclusions based on similarities.
        """
        conclusion = Proposition("Therefore, A and B have similar features.")
        return f"Analogical Reasoning:\n{p}\n{q}\n{conclusion}\n"


class CaseBasedReasoning:
    @staticmethod
    def reason(p, q):
        """
        Case-based reasoning: Solves new problems based on past similar cases.
        """
        conclusion = Proposition("Therefore, C2 is similar to C1.")
        return f"Case-based Reasoning:\n{p}\n{q}\n{conclusion}\n"


class NonmonotonicReasoning:
    @staticmethod
    def reason(current_knowledge, new_information):
        """
        Nonmonotonic reasoning: Updates conclusions with new evidence.
        """
        updated_knowledge = current_knowledge + [new_information]
        conclusion = Proposition("Therefore, conclusions may change with new information.")
        knowledge_str = '\n'.join(str(knowledge) for knowledge in updated_knowledge)
        return f"Nonmonotonic Reasoning:\n{knowledge_str}\n{conclusion}\n"


class FormalReasoning:
    @staticmethod
    def reason(p, q):
        """
        Formal reasoning: Uses formal logic systems.
        """
        conclusion = Proposition("Therefore, the conclusion follows from the premises.")
        return f"Formal Reasoning:\n{p}\n{q}\n{conclusion}\n"


class InformalReasoning:
    @staticmethod
    def reason(p, q):
        """
        Informal reasoning: Uses everyday language and common sense.
        """
        conclusion = Proposition("Therefore, the conclusion is drawn based on common sense.")
        return f"Informal Reasoning:\n{p}\n{q}\n{conclusion}\n"


class ProbabilisticReasoning:
    @staticmethod
    def reason(p, q):
        """
        Probabilistic reasoning: Uses probability to handle uncertainty.
        """
        conclusion = Proposition("Therefore, the conclusion is drawn based on probability.")
        return f"Probabilistic Reasoning:\n{p}\n{q}\n{conclusion}\n"


class HeuristicReasoning:
    @staticmethod
    def reason(p, q):
        """
        Heuristic reasoning: Uses rules of thumb or shortcuts.
        """
        conclusion = Proposition("Therefore, the conclusion is drawn based on heuristics.")
        return f"Heuristic Reasoning:\n{p}\n{q}\n{conclusion}\n"


class CausalReasoning:
    @staticmethod
    def reason(p, q):
        """
        Causal reasoning: Identifies cause-and-effect relationships.
        """
        conclusion = Proposition("Therefore, there is a cause-and-effect relationship.")
        return f"Causal Reasoning:\n{p}\n{q}\n{conclusion}\n"


class CounterfactualReasoning:
    @staticmethod
    def reason(p, q):
        """
        Counterfactual reasoning: Considers alternative scenarios.
        """
        conclusion = Proposition("Therefore, the conclusion considers an alternative scenario.")
        return f"Counterfactual Reasoning:\n{p}\n{q}\n{conclusion}\n"


class FuzzyReasoning:
    @staticmethod
    def reason(p, q):
        """
        Fuzzy reasoning: Deals with approximate reasoning.
        """
        conclusion = Proposition("Therefore, the conclusion is drawn based on fuzzy logic.")
        return f"Fuzzy Reasoning:\n{p}\n{q}\n{conclusion}\n"


class ModalReasoning:
    @staticmethod
    def reason(p, q):
        """
        Modal reasoning: Considers possibilities and necessities.
        """
        conclusion = Proposition("Therefore, the conclusion considers possibilities and necessities.")
        return f"Modal Reasoning:\n{p}\n{q}\n{conclusion}\n"


class DeonticReasoning:
    @staticmethod
    def reason(p, q):
        """
        Deontic reasoning: Involves norms and obligations.
        """
        conclusion = Proposition("Therefore, the conclusion considers norms and obligations.")
        return f"Deontic Reasoning:\n{p}\n{q}\n{conclusion}\n"


class Reasoning:
    def deductive_reasoning(self, p, q):
        return DeductiveReasoning.reason(p, q)

    def inductive_reasoning(self, observations):
        return InductiveReasoning.reason(observations)

    def abductive_reasoning(self, p, q):
        return AbductiveReasoning.reason(p, q)

    def analogical_reasoning(self, p, q):
        return AnalogicalReasoning.reason(p, q)

    def case_based_reasoning(self, p, q):
        return CaseBasedReasoning.reason(p, q)

    def nonmonotonic_reasoning(self, current_knowledge, new_information):
        return NonmonotonicReasoning.reason(current_knowledge, new_information)

    def formal_reasoning(self, p, q):
        return FormalReasoning.reason(p, q)

    def informal_reasoning(self, p, q):
        return InformalReasoning.reason(p, q)

    def probabilistic_reasoning(self, p, q):
        return ProbabilisticReasoning.reason(p, q)

    def heuristic_reasoning(self, p, q):
        return HeuristicReasoning.reason(p, q)

    def causal_reasoning(self, p, q):
        return CausalReasoning.reason(p, q)

    def counterfactual_reasoning(self, p, q):
        return CounterfactualReasoning.reason(p, q)

    def fuzzy_reasoning(self, p, q):
        return FuzzyReasoning.reason(p, q)

    def modal_reasoning(self, p, q):
        return ModalReasoning.reason(p, q)

    def deontic_reasoning(self, p, q):
        return DeonticReasoning.reason(p, q)

    @staticmethod
    def logical_conclusion():
        return "\nLogical Conclusion: Reasoning with propositions p and q\n" \
               "allows us to make logical inferences and conclusions."


if __name__ == "__main__":
    reasoning = Reasoning()

    # Deductive reasoning example
    p_deductive = Proposition("p: All X are Y.")
    q_deductive = Proposition("q: Z is X.")
    print(reasoning.deductive_reasoning(p_deductive, q_deductive))

    # Inductive reasoning example
    observations_inductive = [
        Proposition("p1: X1 is Y."),
        Proposition("p2: X2 is Y."),
        Proposition("p3: X3 is Y.")
    ]
    print(reasoning.inductive_reasoning(observations_inductive))

    # Abductive reasoning example
    p_abductive = Proposition("p: X is observed.")
    q_abductive = Proposition("q: Y can cause X.")
    print(reasoning.abductive_reasoning(p_abductive, q_abductive))

    # Analogical reasoning example
    p_analogical = Proposition("p: A has feature F.")
    q_analogical = Proposition("q: B has feature F.")
    print(reasoning.analogical_reasoning(p_analogical, q_analogical))

    # Case-based reasoning example
    p_case_based = Proposition("p: Case C1 has properties P1, P2, P3.")
    q_case_based = Proposition("q: New case C2 has properties P1, P2, P3.")
    print(reasoning.case_based_reasoning(p_case_based, q_case_based))

    # Nonmonotonic reasoning example
    current_knowledge_nonmonotonic = [
        Proposition("p: All birds can fly."),
        Proposition("q: Tweety is a bird.")
    ]
    new_information_nonmonotonic = Proposition("r: Tweety is a penguin.")
    print(reasoning.nonmonotonic_reasoning(current_knowledge_nonmonotonic, new_information_nonmonotonic))

    # Logical conclusion
    print(reasoning.logical_conclusion())

class THOT:
    """
    Tapestry of thought. THOT dispatches an input across the reasoning styles
    defined above and gathers each perspective into a single tapestry of results.
    """

    # reasoning-style classes defined above, keyed by style name
    STYLES = {
        "deductive": DeductiveReasoning,
        "inductive": InductiveReasoning,
        "abductive": AbductiveReasoning,
        "analogical": AnalogicalReasoning,
        "case_based": CaseBasedReasoning,
        "nonmonotonic": NonmonotonicReasoning,
        "formal": FormalReasoning,
        "informal": InformalReasoning,
        "probabilistic": ProbabilisticReasoning,
        "heuristic": HeuristicReasoning,
        "causal": CausalReasoning,
        "counterfactual": CounterfactualReasoning,
        "fuzzy": FuzzyReasoning,
        "modal": ModalReasoning,
        "deontic": DeonticReasoning,
    }

    def __init__(self, chatter=None, reasoners=None):
        self.chatter = chatter
        self.reasoners = dict(reasoners) if reasoners is not None else dict(self.STYLES)
        # SocraticReasoning refinement is available only when a chatter is supplied
        self.socratic_reasoner = SocraticReasoning(self.chatter) if self.chatter is not None else None
        self.thot_log_path = './mindx/thots.json'
        self.initialize_thot_log()

    def initialize_thot_log(self):
        if not os.path.exists('./mindx'):
            os.makedirs('./mindx')
        if not os.path.exists(self.thot_log_path):
            with open(self.thot_log_path, 'w') as file:
                json.dump([], file)

    def log_thot(self, thot_data):
        with open(self.thot_log_path, 'r') as file:
            thots = json.load(file)
        thots.append(thot_data)
        with open(self.thot_log_path, 'w') as file:
            json.dump(thots, file, indent=4)

    def think(self, input_text, styles=None):
        """
        Dispatch input_text across the selected reasoning styles.

        Args:
            input_text: the statement to reason about.
            styles: optional list of style names; defaults to every reasoner.

        Returns:
            dict: {style_name: result} for each reasoning style applied.
        """
        proposition = Proposition(input_text)
        selected = styles if styles is not None else list(self.reasoners)
        results = {}
        for name in selected:
            reasoner = self.reasoners.get(name)
            if reasoner is None:
                logging.warning(f"Unknown reasoning style: {name}")
                continue
            try:
                if name == "inductive":
                    results[name] = reasoner.reason([proposition])
                elif name == "nonmonotonic":
                    results[name] = reasoner.reason([proposition], proposition)
                else:
                    results[name] = reasoner.reason(proposition, proposition)
            except Exception as e:
                logging.error(f"Error in {name} reasoning: {e}")
                results[name] = f"Error: {e}"
        self.log_thot({"input": input_text, "results": results})
        return results

    def combine_results(self, proposition_p, proposition_q):
        combined_results = []
        for name, reasoner in self.reasoners.items():
            try:
                if name == "inductive":
                    result = reasoner.reason([proposition_p, proposition_q])
                elif name == "nonmonotonic":
                    result = reasoner.reason([proposition_p], proposition_q)
                else:
                    result = reasoner.reason(proposition_p, proposition_q)
                combined_results.append(result)
            except Exception as e:
                logging.error(f"Error in {name} reasoning: {e}")
        return combined_results

    def make_decision(self, combined_results):
        if self.chatter is None:
            raise ValueError("THOT requires a chatter instance to make a decision.")
        decision = self.chatter.generate_response("\n".join(combined_results))
        return decision

    def refine_decision(self, decision):
        if self.socratic_reasoner is None:
            raise ValueError("THOT requires a chatter instance to refine a decision.")
        self.socratic_reasoner.add_premise(decision)
        refined_decision = self.socratic_reasoner.draw_conclusion()
        return refined_decision


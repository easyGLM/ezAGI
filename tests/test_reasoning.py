# SocraticReasoning end-to-end with a mock chatter — no keys, no network
import json
import pathlib

from automind.SocraticReasoning import SocraticReasoning


def test_draw_conclusion_end_to_end(mock_chatter):
    reasoning = SocraticReasoning(mock_chatter)
    events = []
    reasoning.on_event = lambda kind, payload: events.append((kind, payload))

    reasoning.add_premise("All humans are mortal.")
    reasoning.add_premise("Socrates is a human.")
    conclusion = reasoning.draw_conclusion()

    assert conclusion == mock_chatter.response
    assert reasoning.premises == []  # cleared for the next round
    assert reasoning.last_confidence == 0.9  # LLM-judged VALID

    kinds = [kind for kind, _ in events]
    assert "premise" in kinds
    assert "generated_premise" in kinds
    assert "validation" in kinds
    assert kinds[-1] == "conclusion"


def test_validated_truth_recorded(mock_chatter):
    reasoning = SocraticReasoning(mock_chatter)
    reasoning.add_premise("water is wet")
    reasoning.draw_conclusion()

    truth_file = pathlib.Path("memory/logs/truth.json")
    assert truth_file.exists()
    data = json.loads(truth_file.read_text())
    assert isinstance(data, list)
    assert data[-1]["truth"] == mock_chatter.response
    assert data[-1]["confidence"] == 0.9

    # a second conclusion must keep the file a valid JSON array (regression)
    reasoning.add_premise("fire is hot")
    reasoning.draw_conclusion()
    data = json.loads(truth_file.read_text())
    assert len(data) == 2


def test_unvalidated_conclusion_not_saved_as_truth(mock_chatter):
    class InvalidJudge(type(mock_chatter)):
        def _answer(self, knowledge):
            if "Answer exactly VALID or INVALID" in knowledge:
                return "INVALID"
            return self.response

    judge = InvalidJudge()
    reasoning = SocraticReasoning(judge)
    reasoning.add_premise("something dubious")
    reasoning.draw_conclusion()

    assert reasoning.last_confidence == 0.3
    truth_file = pathlib.Path("memory/logs/truth.json")
    assert not truth_file.exists()
    notpremise = json.loads(pathlib.Path("memory/logs/notpremise.json").read_text())
    assert any("Unvalidated conclusion" in entry["message"] for entry in notpremise)


def test_streaming_token_hook(mock_chatter):
    reasoning = SocraticReasoning(mock_chatter)
    tokens = []
    reasoning.on_token = tokens.append
    reasoning.add_premise("stream me")
    conclusion = reasoning.draw_conclusion()
    assert "".join(tokens).strip() == conclusion

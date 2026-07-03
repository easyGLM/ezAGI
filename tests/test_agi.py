# FundamentalAGI pipeline with a mock chatter
from automind.automind import FundamentalAGI


def test_get_conclusion_from_agi(mock_chatter):
    agi = FundamentalAGI(mock_chatter)
    conclusion = agi.get_conclusion_from_agi("why is the sky blue")
    assert conclusion == mock_chatter.response
    assert agi.agi.reasoning.premises == []


def test_learn_from_data(mock_chatter):
    from automind.agi import AGI
    agi = AGI(mock_chatter)
    p, q = agi.learn_from_data("the ocean is salty")
    assert p == "the ocean is salty"
    assert isinstance(q, str) and q  # chatter-generated supporting premise

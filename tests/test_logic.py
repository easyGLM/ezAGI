# truth tables, tautology, and the safe expression evaluator
import pytest

from automind.logic import LogicTables, SafeBooleanEvaluator


@pytest.fixture
def tables():
    lt = LogicTables()
    lt.add_variable("A")
    lt.add_variable("B")
    return lt


def test_truth_table_rows(tables):
    tables.add_expression("A and B")
    table = tables.generate_truth_table()
    assert len(table) == 4
    assert sum(1 for row in table if row["A and B"]) == 1


def test_tautology_true(tables):
    assert tables.tautology("A or not A") is True


def test_tautology_false(tables):
    assert tables.tautology("A and not A") is False


def test_infix_rewrites():
    evaluator = SafeBooleanEvaluator({"A": True, "B": False})
    assert evaluator.evaluate("A xor B") is True
    assert evaluator.evaluate("A nand B") is True
    assert evaluator.evaluate("A nor B") is False
    assert evaluator.evaluate("A implication B") is False
    assert evaluator.evaluate("B implication A") is True


def test_safe_evaluator_rejects_injection(tables):
    assert tables.evaluate_expression("__import__('os').system('true')", {"A": True}) is False
    assert tables.evaluate_expression("(lambda: 1)()", {"A": True}) is False
    assert tables.evaluate_expression("A.__class__", {"A": True}) is False


def test_is_propositional(tables):
    assert tables.is_propositional("A and B") is True
    assert tables.is_propositional("the sky is blue") is False


def test_unify_variables_with_strings(tables):
    assert tables.unify_variables("Socrates is a man", "socrates is a man") is True
    assert tables.unify_variables("Socrates is a man", "all men are mortal") is False

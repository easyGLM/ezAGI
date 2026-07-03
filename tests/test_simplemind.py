# SimpleMind/coach — runs only when the [learn] extras are installed
import json
import pathlib

import pytest

jax = pytest.importorskip("jax")
pytest.importorskip("optax")


def test_simplemind_trains_and_loss_decreases():
    import numpy as np
    from simplemind.SimpleMind import SimpleMind

    x = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    y = np.array([[0], [1], [1], [0]], dtype=float)
    net = SimpleMind(input_size=2, hidden_sizes=[8], output_size=1, learning_rate=0.05)
    first_loss = float(net._loss_fn(net.params, x, y))
    net.train(x, y, epochs=200)
    final_loss = float(net._loss_fn(net.params, x, y))
    prediction = net.predict(x)
    assert prediction.shape == (4, 1)
    assert final_loss < first_loss


def test_coach_loads_both_stm_schemas():
    from simplemind.coach import Coach

    stm = pathlib.Path("memory/stm")
    stm.mkdir(parents=True, exist_ok=True)
    (stm / "1.json").write_text(json.dumps(
        {"instruction": "what is ezAGI", "response": "augmented intelligence"}))
    (stm / "2memory.json").write_text(json.dumps(
        {"dialog": {"instruction": "who is codephreak", "response": "the author"}}))

    coach = Coach(model=None)
    beliefs = coach.load_beliefs()
    assert len(beliefs) == 2

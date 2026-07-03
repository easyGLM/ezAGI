# every module in the six packages plus both entry points must import
import importlib

import pytest

MODULES = [
    "memory.memory",
    "webmind.api",
    "webmind.chatter",
    "webmind.ollama_handler",
    "webmind.ollama_install",
    "webmind.html_head",
    "automind.logic",
    "automind.SocraticReasoning",
    "automind.agi",
    "automind.automind",
    "automind.openmind",
    "automindx.bdi",
    "automindx.reasoning",
    "automindx.make_decision",
    "automindx.epistemic",
    "automindx.deductive",
    "automindx.fuzzy",
    "automindx.nonmonotonic",
    "automindx.abduction",
    "automindx.prediction",
    "automindx.autonomize",
    "automindx.self_healing",
    "mastermind.controller",
    "mastermind.mastermind",
    "mastermind.SimpleCoder",
    "mastermind.easyAGIcli",
    "simplemind.SimpleMind",
    "simplemind.coach",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_module_imports(module_name):
    importlib.import_module(module_name)


def test_entry_points_import():
    import ezAGI
    import easyAGI  # noqa: F401  (shim: no server starts thanks to the run guard)
    assert hasattr(ezAGI, "run")
    assert ezAGI.openmind is not None

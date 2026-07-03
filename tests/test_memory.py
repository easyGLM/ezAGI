# memory round-trips and the truth.json valid-JSON regression
import json
import pathlib

from memory.memory import (create_memory_folders, store_in_stm, DialogEntry,
                           save_conversation_memory, save_valid_truth, append_json_log)


def test_create_memory_folders():
    create_memory_folders()
    for folder in ("memory/stm", "memory/ltm", "memory/episodic", "memory/truth",
                   "memory/logs", "mindx/agency"):
        assert pathlib.Path(folder).is_dir()


def test_stm_round_trip():
    create_memory_folders()
    store_in_stm(DialogEntry("what is ezAGI", "easy augmented generative intelligence"))
    files = list(pathlib.Path("memory/stm").glob("*.json"))
    assert files
    data = json.loads(files[0].read_text())
    assert data["instruction"] == "what is ezAGI"
    assert data["response"] == "easy augmented generative intelligence"


def test_save_conversation_memory_schema():
    save_conversation_memory({"dialog": {"instruction": "q", "response": "a"}})
    files = list(pathlib.Path("memory/stm").glob("*memory.json"))
    assert files
    data = json.loads(files[0].read_text())
    assert data["dialog"]["instruction"] == "q"


def test_append_json_log_is_always_valid_json():
    path = "memory/logs/truth.json"
    append_json_log(path, {"truth": "one", "confidence": 0.9})
    append_json_log(path, {"truth": "two", "confidence": 1.0})
    data = json.loads(pathlib.Path(path).read_text())
    assert isinstance(data, list) and len(data) == 2
    assert data[1]["truth"] == "two"


def test_append_json_log_recovers_from_corrupt_file():
    path = pathlib.Path("memory/logs/truth.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"truth": "legacy"}{"truth": "corrupt-concatenated"}')
    append_json_log(str(path), {"truth": "fresh"})
    data = json.loads(path.read_text())
    assert isinstance(data, list)
    assert data[-1]["truth"] == "fresh"


def test_save_valid_truth_writes_file():
    create_memory_folders()
    save_valid_truth({"truth": "validated", "confidence": 0.9, "timestamp": "now"})
    files = list(pathlib.Path("memory/truth").glob("*.json"))
    assert any(json.loads(f.read_text()).get("truth") == "validated" for f in files)

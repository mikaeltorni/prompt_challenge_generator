"""Public entrypoint integration tests with model calls replaced by fixtures."""

from importlib import import_module, util
import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_entrypoint(monkeypatch, tmp_path, *argv):
    """Load main.py with isolated CLI, environment, and dotenv behavior."""
    client_config = import_module("src.ClientConfig")
    monkeypatch.setattr(client_config, "load_dotenv", Mock())
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only-key")
    monkeypatch.setattr(sys, "argv", ["main.py", *argv])
    monkeypatch.chdir(PROJECT_ROOT)
    spec = util.spec_from_file_location(
        "prompt_challenge_generator_entrypoint_under_test", PROJECT_ROOT / "main.py"
    )
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.chdir(tmp_path)
    return module


def test_main_runs_the_complete_pipeline_without_network_calls(tmp_path, monkeypatch):
    module = load_entrypoint(
        monkeypatch,
        tmp_path,
        "--theme",
        "Polar expeditions",
        "--tcCount",
        "2",
        "--alias",
        "  Arctic Trips  ",
        "--n",
        "1",
        "--max_concurrent",
        "2",
    )
    monkeypatch.setattr(module, "next_iteration_numbers", Mock(return_value=[7]))
    problem = "Suggest a safe polar expedition."
    cases = json.dumps(
        [
            {"input": "Plan a route", "expected_output": "Route A"},
            {"input": "Unsafe route", "expected_output": "invalid_question"},
        ]
    )
    problem_agent = module.agent_config.problem_statement_generator
    example_agent = module.agent_config.example_generator
    parameter_agent = module.agent_config.parameter_generator
    test_agent = module.agent_config.test_case_generator
    problem_agent.send_message = Mock(return_value=problem)
    example_agent.send_message = Mock(return_value="Example response")
    parameter_agent.send_message = Mock(return_value="Parameter response")
    test_agent.send_message = Mock(return_value=cases)

    module.main()

    challenge_dir = tmp_path / "generated_challenges" / "arctic-trips-007"
    assert (challenge_dir / "problem_statement").read_text(encoding="utf-8") == problem + "\n"
    assert (challenge_dir / "examples").read_text(encoding="utf-8") == "Example response\n"
    assert (challenge_dir / "parameter").read_text(encoding="utf-8") == "Parameter response\n"
    generated_cases = json.loads(
        (challenge_dir / "test_cases").read_text(encoding="utf-8")
    )
    assert generated_cases == json.loads(cases)
    assert (challenge_dir / "eval_test.yaml").is_file()
    assert (challenge_dir / "EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md").is_file()
    assert (challenge_dir / "iteration.log").is_file()
    problem_agent.send_message.assert_called_once_with("Polar expeditions")
    example_agent.send_message.assert_called_once_with(problem)
    parameter_agent.send_message.assert_called_once_with(problem)
    test_agent.send_message.assert_called_once_with(
        "Produce exactly 2 test cases with the following problem statement:\n" + problem
    )


@pytest.mark.parametrize("max_concurrent", [1, 2, 9])
def test_main_caps_workers_at_requested_and_total_run_count(
    tmp_path, monkeypatch, max_concurrent
):
    module = load_entrypoint(
        monkeypatch,
        tmp_path,
        "--theme",
        "Theme",
        "--n",
        "3",
        "--max_concurrent",
        str(max_concurrent),
    )
    monkeypatch.setattr(module, "next_iteration_numbers", Mock(return_value=[10, 11, 12]))
    workers = []

    class RecordingExecutor:
        def __init__(self, max_workers):
            workers.append(max_workers)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def submit(self, function, run_number):
            from concurrent.futures import Future

            future = Future()
            try:
                future.set_result(function(run_number))
            except Exception as exc:
                future.set_exception(exc)
            return future

    monkeypatch.setattr(module.concurrent.futures, "ThreadPoolExecutor", RecordingExecutor)
    generated = []
    monkeypatch.setattr(module, "_generate_single_challenge", generated.append)

    module.main()

    assert workers == [min(max_concurrent, 3)]
    assert generated == [1, 2, 3]
    assert module.iteration_assignments == {1: 10, 2: 11, 3: 12}

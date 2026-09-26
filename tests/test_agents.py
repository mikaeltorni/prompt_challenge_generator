"""Agent request construction and client configuration tests."""

from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.Agent import Agent
from src.AgentConfig import AgentConfig


def test_agent_loads_a_system_prompt_from_the_prompts_directory(tmp_path, monkeypatch):
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "system.md").write_text("  Follow the contract.\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    agent = Agent(object(), "Example Agent", "test-model", "system.md")

    assert agent.system_prompt == "  Follow the contract.\n"
    assert agent.model == "test-model"
    assert agent.temperature == 0
    assert agent.max_tokens == 16384


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (SimpleNamespace(content="A result"), "A result"),
        (None, ""),
        (SimpleNamespace(content=None), ""),
    ],
)
def test_agent_send_message_returns_completion_content(
    message, expected, tmp_path, monkeypatch
):
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "unused.md").write_text("system prompt", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    create = Mock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=message)]))
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    agent = Agent(
        client,
        "Test Agent",
        "test-model",
        "unused.md",
        temperature=0.25,
        max_tokens=77,
    )
    agent.system_prompt = "system instructions"

    result = agent.send_message("multi word user input")

    assert result == expected
    create.assert_called_once_with(
        model="test-model",
        messages=[
            {"role": "system", "content": "system instructions"},
            {"role": "user", "content": "multi word user input"},
        ],
        temperature=0.25,
        max_tokens=77,
    )


def test_agent_config_builds_all_four_project_agents(monkeypatch):
    constructed = []

    class FakeAgent:
        def __init__(self, *args, **kwargs):
            constructed.append((args, kwargs))

    agent_config_module = import_module("src.AgentConfig")
    monkeypatch.setattr(agent_config_module, "Agent", FakeAgent)

    config = AgentConfig("fake-client")

    assert len(constructed) == 4
    assert [call[0][1] for call in constructed] == [
        "Challenge Generator",
        "Example Generator",
        "Parameter Generator",
        "Test Case Generator",
    ]
    assert all(call[0][0] == "fake-client" for call in constructed)
    assert all(call[0][2] == "openai/gpt-5-nano" for call in constructed)
    assert constructed[-1][1] == {"max_tokens": 128000}
    assert isinstance(config.problem_statement_generator, FakeAgent)
    assert isinstance(config.example_generator, FakeAgent)
    assert isinstance(config.parameter_generator, FakeAgent)
    assert isinstance(config.test_case_generator, FakeAgent)


def test_client_config_requires_an_api_key(monkeypatch, tmp_path):
    client_config_module = import_module("src.ClientConfig")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    load_dotenv = Mock()
    monkeypatch.setattr(client_config_module, "load_dotenv", load_dotenv)

    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY is missing"):
        client_config_module.ClientConfig()

    load_dotenv.assert_called_once_with(dotenv_path=Path(".env"), override=False)


def test_client_config_uses_openrouter_endpoint_and_environment_key(monkeypatch, tmp_path):
    client_config_module = import_module("src.ClientConfig")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only-key")
    monkeypatch.setattr(client_config_module, "load_dotenv", Mock())

    client = client_config_module.ClientConfig()

    assert str(client.base_url).rstrip("/") == "https://openrouter.ai/api/v1"
    assert client.api_key == "test-only-key"

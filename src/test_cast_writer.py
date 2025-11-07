from __future__ import annotations

import json
import os
from pathlib import Path

from src.logger import ProjectLogger

DEFAULT_MODEL = "openrouter:openai/gpt-4.1"
logger = ProjectLogger("test_cast_writer.py")


def first_non_empty_line(path: Path) -> str:
    logger.entry("first_non_empty_line", path=path)
    if not path.exists():
        result = path.stem
    else:
        result = path.stem
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                result = stripped
                break
    logger.exit("first_non_empty_line", line=result)
    return result


def quote_yaml(value: str) -> str:
    logger.entry("quote_yaml", value=value)
    escaped = value.replace('"', '\\"')
    quoted = f'"{escaped}"'
    logger.exit("quote_yaml", quoted=quoted)
    return quoted


def load_test_cases(path: Path) -> list[dict[str, str]]:
    logger.entry("load_test_cases", path=path)
    if not path.exists():
        error_message = f"Missing test_cases file in {path.parent}"
        raise FileNotFoundError(error_message)

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        error_message = f"No test cases found in {path}"
        raise ValueError(error_message)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        error_message = f"test_cases must be valid JSON: {exc}"
        raise ValueError(error_message) from exc

    if not isinstance(data, list):
        error_message = "test_cases must be a JSON array."
        raise ValueError(error_message)

    cases: list[dict[str, str]] = []
    for entry in data:
        if not isinstance(entry, dict):
            error_message = "Each test case must be an object with `input` and `expected_output` keys."
            raise ValueError(error_message)
        if "input" not in entry or "expected_output" not in entry:
            error_message = "Each test case must include `input` and `expected_output` keys."
            raise ValueError(error_message)

        input_val = entry["input"]
        expected_val = entry["expected_output"]

        if not isinstance(input_val, str) or not isinstance(expected_val, str):
            error_message = "`input` and `expected_output` must be strings."
            raise ValueError(error_message)

        cases.append({"input": input_val, "expected_output": expected_val})

    logger.exit("load_test_cases", cases=cases)
    return cases


def write_user_prompt_placeholder(destination: Path):
    logger.entry("write_user_prompt_placeholder", destination=destination)
    helper = "\n".join(
        [
            "# Edit this prompt to beat the challenge",
        ]
    )
    destination.write_text(helper, encoding="utf-8")
    logger.exit("write_user_prompt_placeholder", return_value=None)


def generate_promptfoo_test_cases(challenge_dir: Path) -> Path:
    logger.entry("generate_promptfoo_test_cases", challenge_dir=challenge_dir)
    challenge_dir = challenge_dir.resolve()

    problem_path = challenge_dir / "problem_statement"
    evaluation_prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "evaluation_prompt.md"
    evaluation_prompt_relpath = Path(os.path.relpath(evaluation_prompt_path, challenge_dir))
    test_cases_path = challenge_dir / "test_cases"
    description = first_non_empty_line(problem_path)

    user_prompt_path = challenge_dir / "EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md"
    write_user_prompt_placeholder(
        user_prompt_path,
    )

    test_cases = load_test_cases(test_cases_path)

    prompt_raw = "{{user_prompt}}"
    eval_prompt_placeholder = "{{eval_prompt}}"

    eval_test_path = challenge_dir / "eval_test.yaml"
    yaml_lines = [
        f"description: {quote_yaml(description)}",
        "",
        "providers:",
        f"  - id: {DEFAULT_MODEL}",
        "    config:",
        "      temperature: 0",
        "      max_tokens: 8192",
        "",
        "defaultTest:",
        "  options:",
        f"    provider: {DEFAULT_MODEL}",
        "",
        "prompts:",
        "  - id: challenge",
        "    label: challenge",
        f"    raw: {quote_yaml(prompt_raw)}",
        "",
        "tests:",
    ]

    for index, case in enumerate(test_cases, start=1):
        scenario = case["input"]
        if len(scenario) > 60:
            scenario = scenario[:57].rstrip() + "..."
        case_description = f"Case {index}: {scenario}"
        yaml_lines.extend(
            [
                f"  - description: {quote_yaml(case_description)}",
                "    vars:",
                f"      user_prompt: file://{user_prompt_path.name}",
                f"      eval_prompt: file://{evaluation_prompt_relpath.as_posix()}",
                f"      input: {quote_yaml(case['input'])}",
                f"      expected_output: {quote_yaml(case['expected_output'])}",
                "    assert:",
                "      - type: llm-rubric",
                f"        value: {quote_yaml(eval_prompt_placeholder)}",
            ]
        )
    yaml_lines.append("")

    eval_test_path.write_text("\n".join(yaml_lines), encoding="utf-8")
    logger.exit("generate_promptfoo_test_cases", eval_test_path=eval_test_path)
    return eval_test_path

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_MODEL = "openrouter:openai/gpt-4.1"

def first_non_empty_line(path: Path) -> str:
    if not path.exists():
        return path.stem
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return path.stem

def quote_yaml(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'

def load_test_cases(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing test_cases file in {path.parent}")

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError(f"No test cases found in {path}")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"test_cases must be valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("test_cases must be a JSON array.")

    cases: list[dict[str, str]] = []
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("Each test case must be an object with `input` and `expected_output` keys.")
        if "input" not in entry or "expected_output" not in entry:
            raise ValueError("Each test case must include `input` and `expected_output` keys.")

        input_val = entry["input"]
        expected_val = entry["expected_output"]

        if not isinstance(input_val, str) or not isinstance(expected_val, str):
            raise ValueError("`input` and `expected_output` must be strings.")

        cases.append({"input": input_val, "expected_output": expected_val})

    return cases

def write_user_prompt_placeholder(destination: Path):
    helper = "\n".join(
        [
            "# Edit this prompt to beat the challenge",
        ]
    )
    destination.write_text(helper, encoding="utf-8")

def generate_promptfoo_test_cases(challenge_dir: Path) -> Path:
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
    if len(test_cases) != 10:
        raise ValueError(
            f"Expected exactly 10 test cases, found {len(test_cases)} in {test_cases_path}"
        )

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
    return eval_test_path

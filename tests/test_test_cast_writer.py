"""Test-case JSON validation and promptfoo asset generation tests."""

import json

import pytest

from src import test_cast_writer as writer


def test_first_non_empty_line_returns_trimmed_description(tmp_path):
    path = tmp_path / "problem_statement"
    path.write_text("\n  First line  \nsecond line\n", encoding="utf-8")

    assert writer.first_non_empty_line(path) == "First line"


def test_first_non_empty_line_falls_back_to_stem_for_blank_or_missing_file(tmp_path):
    blank = tmp_path / "blank_statement"
    blank.write_text(" \n\t\n", encoding="utf-8")

    assert writer.first_non_empty_line(blank) == "blank_statement"
    assert writer.first_non_empty_line(tmp_path / "missing_statement") == "missing_statement"


@pytest.mark.parametrize(
    "value",
    [
        "simple text",
        """quotes: "double" and 'single'""",
        r"Windows path C:\\new\\folder",
        "line one\nline two\tend",
        "München 東京",
    ],
)
def test_quote_yaml_preserves_arbitrary_string_values(value):
    assert json.loads(writer.quote_yaml(value)) == value


def test_load_test_cases_accepts_valid_string_pairs(tmp_path):
    path = tmp_path / "test_cases"
    expected = [
        {"input": "valid request", "expected_output": "valid answer"},
        {"input": "invalid request", "expected_output": "invalid_question"},
    ]
    path.write_text(json.dumps(expected), encoding="utf-8")

    assert writer.load_test_cases(path) == expected


def test_load_test_cases_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="Missing test_cases file"):
        writer.load_test_cases(tmp_path / "test_cases")


def test_load_test_cases_rejects_empty_file(tmp_path):
    path = tmp_path / "test_cases"
    path.write_text("  \n", encoding="utf-8")

    with pytest.raises(ValueError, match="No test cases found"):
        writer.load_test_cases(path)


def test_load_test_cases_rejects_malformed_json(tmp_path):
    path = tmp_path / "test_cases"
    path.write_text("[{", encoding="utf-8")

    with pytest.raises(ValueError, match="must be valid JSON"):
        writer.load_test_cases(path)


def test_load_test_cases_rejects_non_array_json(tmp_path):
    path = tmp_path / "test_cases"
    path.write_text('{"input": "one"}', encoding="utf-8")

    with pytest.raises(ValueError, match="must be a JSON array"):
        writer.load_test_cases(path)


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ('["not an object"]', "Each test case must be an object"),
        ('[{"input": "only input"}]', "must include `input` and `expected_output`"),
        ('[{"expected_output": "only output"}]', "must include `input` and `expected_output`"),
        ('[{"input": 7, "expected_output": "text"}]', "must be strings"),
        ('[{"input": "text", "expected_output": null}]', "must be strings"),
    ],
)
def test_load_test_cases_rejects_invalid_case_shapes(tmp_path, raw, message):
    path = tmp_path / "test_cases"
    path.write_text(raw, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        writer.load_test_cases(path)


def test_write_user_prompt_placeholder_creates_expected_instructions(tmp_path):
    destination = tmp_path / "EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md"

    writer.write_user_prompt_placeholder(destination)

    assert destination.read_text(encoding="utf-8") == "# Edit this prompt to beat the challenge"


def test_generate_promptfoo_assets_from_valid_cases(tmp_path):
    challenge_dir = tmp_path / "generated" / "trip-planning-001"
    challenge_dir.mkdir(parents=True)
    (challenge_dir / "problem_statement").write_text(
        "\n  Plan a trip\nAdditional context", encoding="utf-8"
    )
    cases = [
        {"input": "Which city?", "expected_output": "Helsinki"},
        {"input": "x" * 80, "expected_output": "invalid_question"},
    ]
    (challenge_dir / "test_cases").write_text(json.dumps(cases), encoding="utf-8")

    output = writer.generate_promptfoo_test_cases(challenge_dir)

    assert output == challenge_dir / "eval_test.yaml"
    assert output.is_file()
    assert (challenge_dir / "EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md").is_file()
    yaml_text = output.read_text(encoding="utf-8")
    assert 'description: "Plan a trip"' in yaml_text
    assert "openrouter:openai/gpt-4.1" in yaml_text
    assert 'raw: "{{user_prompt}}"' in yaml_text
    assert "file://EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md" in yaml_text
    assert "evaluation_prompt.md" in yaml_text
    assert f"input: {writer.quote_yaml(cases[0]['input'])}" in yaml_text
    expected_output = writer.quote_yaml(cases[0]["expected_output"])
    assert f"expected_output: {expected_output}" in yaml_text
    assert 'description: "Case 2: ' + ("x" * 57) + '..."' in yaml_text
    assert yaml_text.count("type: llm-rubric") == 2


def test_generate_promptfoo_assets_serializes_newlines_and_backslashes(tmp_path):
    challenge_dir = tmp_path / "challenge"
    challenge_dir.mkdir()
    (challenge_dir / "problem_statement").write_text("Line handling", encoding="utf-8")
    case = {"input": "C:\\new\\line\nnext", "expected_output": 'say "hello"\\now'}
    (challenge_dir / "test_cases").write_text(json.dumps([case]), encoding="utf-8")

    output = writer.generate_promptfoo_test_cases(challenge_dir)
    yaml_text = output.read_text(encoding="utf-8")

    assert f"input: {json.dumps(case['input'], ensure_ascii=False)}" in yaml_text
    assert f"expected_output: {json.dumps(case['expected_output'], ensure_ascii=False)}" in yaml_text


def test_generate_promptfoo_assets_creates_placeholder_before_validation_error(tmp_path):
    challenge_dir = tmp_path / "challenge"
    challenge_dir.mkdir()
    (challenge_dir / "problem_statement").write_text("Challenge", encoding="utf-8")
    (challenge_dir / "test_cases").write_text("not json", encoding="utf-8")

    with pytest.raises(ValueError, match="must be valid JSON"):
        writer.generate_promptfoo_test_cases(challenge_dir)

    assert (challenge_dir / "EDIT_THIS_PROMPT_TO_BEAT_THE_CHALLENGE.md").is_file()
    assert not (challenge_dir / "eval_test.yaml").exists()

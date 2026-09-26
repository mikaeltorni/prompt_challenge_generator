"""CLI argument parsing and validation tests."""

import sys

import pytest

from src.Args import Args


def parse_args(monkeypatch, *argv):
    """Construct Args using an isolated command line."""
    monkeypatch.setattr(sys, "argv", ["main.py", *argv])
    return Args()


def test_required_theme_accepts_multiword_value_and_strips_whitespace(monkeypatch):
    args = parse_args(monkeypatch, "--theme", "  Northern lights  ")

    assert args.theme == "Northern lights"


def test_optional_arguments_have_documented_defaults(monkeypatch):
    args = parse_args(monkeypatch, "--theme", "Ocean travel")

    assert args.test_case_count == 50
    assert args.alias is None
    assert args.n == 1
    assert args.max_concurrent == 1


def test_optional_arguments_parse_values_and_trim_alias(monkeypatch):
    args = parse_args(
        monkeypatch,
        "--theme",
        "Space exploration",
        "--tcCount",
        "18",
        "--alias",
        "  Cosmos  ",
        "--n",
        "4",
        "--max_concurrent",
        "2",
    )

    assert args.test_case_count == 18
    assert args.alias == "Cosmos"
    assert args.n == 4
    assert args.max_concurrent == 2


@pytest.mark.parametrize("theme", ["", "   "])
def test_empty_theme_is_rejected(monkeypatch, theme):
    with pytest.raises(ValueError, match="Theme cannot be empty"):
        parse_args(monkeypatch, "--theme", theme)


def test_theme_is_required(monkeypatch):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(monkeypatch)

    assert exc_info.value.code == 2


@pytest.mark.parametrize("alias", ["", "   "])
def test_empty_alias_is_rejected(monkeypatch, alias):
    with pytest.raises(ValueError, match="Alias cannot be empty"):
        parse_args(monkeypatch, "--theme", "Travel", "--alias", alias)


def test_test_case_count_must_be_an_integer(monkeypatch):
    with pytest.raises(ValueError):
        parse_args(monkeypatch, "--theme", "Travel", "--tcCount", "many")


@pytest.mark.parametrize("count", ["0", "-1"])
def test_generation_count_must_be_positive(monkeypatch, count):
    with pytest.raises(ValueError, match="--n must be greater than or equal to 1"):
        parse_args(monkeypatch, "--theme", "Travel", "--n", count)


@pytest.mark.parametrize("count", ["0", "-3"])
def test_max_concurrent_must_be_positive(monkeypatch, count):
    with pytest.raises(
        ValueError,
        match="--max_concurrent must be greater than or equal to 1",
    ):
        parse_args(monkeypatch, "--theme", "Travel", "--max_concurrent", count)


def test_batch_arguments_must_be_integers(monkeypatch):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(monkeypatch, "--theme", "Travel", "--n", "two")

    assert exc_info.value.code == 2

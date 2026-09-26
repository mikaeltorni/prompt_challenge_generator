"""Section normalization and persistence tests."""

from src import file_manager, section_splitter


def test_normalize_section_name_trims_and_lowercases_names():
    assert section_splitter._normalize_section_name("  Test_Cases  ") == "test_cases"


def test_normalize_section_name_accepts_tuple_and_list_values():
    assert section_splitter._normalize_section_name((" Examples ", "ignored")) == "examples"
    assert section_splitter._normalize_section_name([" Parameter "]) == "parameter"


def test_normalize_section_name_falls_back_to_string_conversion():
    assert section_splitter._normalize_section_name(42) == "42"
    assert section_splitter._normalize_section_name([]) == "[]"


def test_save_section_writes_content_and_returns_path(tmp_path):
    target_dir = tmp_path / "challenge"
    target_dir.mkdir()

    content, returned_dir = section_splitter.save_section(
        "Solve the stated task.", "Theme", " Problem_Statement ", target_dir
    )

    assert content == "Solve the stated task."
    assert returned_dir == target_dir
    assert (target_dir / "problem_statement").read_text(encoding="utf-8") == (
        "Solve the stated task.\n"
    )


def test_save_section_writes_empty_content_as_an_empty_file(tmp_path):
    target_dir = tmp_path / "challenge"
    target_dir.mkdir()

    section_splitter.save_section("", "Theme", "examples", target_dir)

    assert (target_dir / "examples").read_text(encoding="utf-8") == ""


def test_save_section_can_return_none(tmp_path):
    target_dir = tmp_path / "challenge"
    target_dir.mkdir()

    result = section_splitter.save_section(
        "cases", "Theme", "test_cases", target_dir, return_value=False
    )

    assert result is None
    assert (target_dir / "test_cases").read_text(encoding="utf-8") == "cases\n"


def test_save_section_creates_directory_using_alias_and_iteration(tmp_path, monkeypatch):
    monkeypatch.setattr(file_manager, "base_dir", tmp_path / "generated")

    content, target_dir = section_splitter.save_section(
        "A challenge", "Long theme name", "problem_statement", alias="Theme Alias", iteration=9
    )

    assert content == "A challenge"
    assert target_dir == tmp_path / "generated" / "theme-alias-009"
    assert (target_dir / "problem_statement").read_text(encoding="utf-8") == (
        "A challenge\n"
    )

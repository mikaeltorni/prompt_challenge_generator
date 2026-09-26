"""Challenge slug, iteration allocation, and directory creation tests."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from src import file_manager


def test_sanitize_theme_produces_lowercase_hyphenated_slug():
    assert file_manager.sanitize_theme("  Café & City Trips! ") == "caf-city-trips"


def test_sanitize_theme_uses_fallback_for_empty_slug():
    assert file_manager.sanitize_theme("--- !!! ---") == "challenge"


def test_next_iteration_numbers_starts_at_one_and_allocates_a_batch(tmp_path, monkeypatch):
    monkeypatch.setattr(file_manager, "base_dir", tmp_path / "generated")

    assert file_manager.next_iteration_numbers("Aurora Viewing", count=3) == [1, 2, 3]
    assert (tmp_path / "generated").is_dir()


def test_next_iteration_numbers_uses_highest_matching_existing_index(tmp_path, monkeypatch):
    base_dir = tmp_path / "generated"
    base_dir.mkdir()
    for name in ("aurora-001", "aurora-004", "aurora-004-extra", "other-009"):
        (base_dir / name).mkdir()
    monkeypatch.setattr(file_manager, "base_dir", base_dir)

    assert file_manager.next_iteration_numbers("Aurora", count=2) == [5, 6]


def test_alias_controls_the_iteration_slug(tmp_path, monkeypatch):
    monkeypatch.setattr(file_manager, "base_dir", tmp_path / "generated")

    assert file_manager.next_iteration_numbers("A long theme", "  My Alias  ") == [1]


def test_next_iteration_numbers_rejects_nonpositive_count(tmp_path, monkeypatch):
    monkeypatch.setattr(file_manager, "base_dir", tmp_path / "generated")

    with pytest.raises(ValueError, match="count must be at least 1"):
        file_manager.next_iteration_numbers("Travel", count=0)


def test_create_theme_directory_uses_next_index_when_unspecified(tmp_path, monkeypatch):
    base_dir = tmp_path / "generated"
    base_dir.mkdir()
    (base_dir / "travel-001").mkdir()
    monkeypatch.setattr(file_manager, "base_dir", base_dir)

    created = file_manager.create_theme_directory("Travel")

    assert created == base_dir / "travel-002"
    assert created.is_dir()


def test_create_theme_directory_honors_alias_and_explicit_iteration(tmp_path, monkeypatch):
    base_dir = tmp_path / "generated"
    monkeypatch.setattr(file_manager, "base_dir", base_dir)

    created = file_manager.create_theme_directory("A long theme", "My Alias", 12)

    assert created == base_dir / "my-alias-012"
    assert created.is_dir()


def test_create_theme_directory_rejects_an_existing_explicit_path(tmp_path, monkeypatch):
    base_dir = tmp_path / "generated"
    (base_dir / "travel-003").mkdir(parents=True)
    monkeypatch.setattr(file_manager, "base_dir", base_dir)

    with pytest.raises(FileExistsError):
        file_manager.create_theme_directory("Travel", iteration=3)


def test_concurrent_directory_creation_allocates_unique_indices(tmp_path, monkeypatch):
    base_dir = tmp_path / "generated"
    monkeypatch.setattr(file_manager, "base_dir", base_dir)

    with ThreadPoolExecutor(max_workers=8) as executor:
        created = list(
            executor.map(
                lambda _: file_manager.create_theme_directory("Travel"), range(16)
            )
        )

    assert len(set(created)) == 16
    assert sorted(path.name for path in created) == [
        f"travel-{index:03d}" for index in range(1, 17)
    ]

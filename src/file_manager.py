import re
import threading
from pathlib import Path
from typing import List

from src.logger import ProjectLogger

base_dir = Path("generated_challenges")
_dir_lock = threading.Lock()
logger = ProjectLogger("file_manager.py")


def sanitize_theme(value: str) -> str:
    logger.entry("sanitize_theme", value=value)
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    result = slug or "challenge"
    logger.exit("sanitize_theme", result=result)
    return result


def _theme_slug(theme, alias):
    slug_source = alias if alias else theme
    return sanitize_theme(slug_source)


def _existing_indices(theme_slug: str) -> List[int]:
    pattern = re.compile(rf"{re.escape(theme_slug)}-(\d{{3}})$")
    return [
        int(match.group(1))
        for entry in base_dir.iterdir()
        if entry.is_dir() and (match := pattern.fullmatch(entry.name))
    ]


def next_iteration_numbers(theme, alias=None, count: int = 1) -> list[int]:
    if count < 1:
        raise ValueError("count must be at least 1.")
    logger.entry("next_iteration_numbers", theme=theme, alias=alias, count=count)
    base_dir.mkdir(parents=True, exist_ok=True)
    with _dir_lock:
        theme_slug = _theme_slug(theme, alias)
        existing_indices = _existing_indices(theme_slug)
        start = max(existing_indices, default=0) + 1
        iterations = [start + offset for offset in range(count)]
    logger.exit("next_iteration_numbers", iterations=iterations)
    return iterations


def create_theme_directory(theme, alias=None, iteration: int | None = None):
    logger.entry("create_theme_directory", theme=theme, alias=alias, iteration=iteration)
    base_dir.mkdir(parents=True, exist_ok=True)

    theme_slug = _theme_slug(theme, alias)

    with _dir_lock:
        if iteration is not None:
            target_dir = base_dir / f"{theme_slug}-{iteration:03d}"
        else:
            existing_indices = _existing_indices(theme_slug)
            iteration = max(existing_indices, default=0) + 1
            target_dir = base_dir / f"{theme_slug}-{iteration:03d}"
        target_dir.mkdir(parents=True, exist_ok=False)

    logger.exit("create_theme_directory", target_dir=target_dir, iteration=iteration)
    return target_dir

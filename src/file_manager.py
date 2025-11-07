import re
import threading
from pathlib import Path

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


def create_theme_directory(theme, alias=None):
    logger.entry("create_theme_directory", theme=theme, alias=alias)
    base_dir.mkdir(parents=True, exist_ok=True)

    slug_source = alias if alias else theme
    theme_slug = sanitize_theme(slug_source)

    with _dir_lock:
        pattern = re.compile(rf"{re.escape(theme_slug)}-(\d{{3}})$")
        existing_indices = [
            int(match.group(1))
            for entry in base_dir.iterdir()
            if entry.is_dir() and (match := pattern.fullmatch(entry.name))
        ]
        next_index = max(existing_indices, default=0) + 1
        target_dir = base_dir / f"{theme_slug}-{next_index:03d}"
        target_dir.mkdir(parents=True, exist_ok=False)

    logger.exit("create_theme_directory", target_dir=target_dir)
    return target_dir

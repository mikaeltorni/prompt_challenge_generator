import re
from pathlib import Path

from src.file_manager import create_theme_directory
from src.logger import ProjectLogger

logger = ProjectLogger("section_splitter.py")

def _normalize_section_name(section_name) -> str:
    logger.entry("_normalize_section_name", section_name=section_name)
    if isinstance(section_name, str):
        normalized = section_name.strip().lower()
    elif isinstance(section_name, (tuple, list)) and section_name:
        normalized = str(section_name[0]).strip().lower()
    else:
        normalized = str(section_name).strip().lower()
    logger.exit("_normalize_section_name", normalized=normalized)
    return normalized

def save_section(
    content,
    theme,
    section_name,
    target_dir: Path | None = None,
    *,
    alias=None,
    return_value=True,
    iteration: int | None = None,
):
    logger.entry(
        "save_section",
        content=content,
        theme=theme,
        section_name=section_name,
        target_dir=target_dir,
        alias=alias,
        return_value=return_value,
        iteration=iteration,
    )
    section_name_str = _normalize_section_name(section_name)
    target_dir = target_dir or create_theme_directory(theme, alias, iteration)

    file_path = target_dir / section_name_str
    text_to_write = f"{content}\n" if content else ""
    file_path.write_text(text_to_write, encoding="utf-8")

    if return_value:
        logger.exit("save_section", content=content, target_dir=target_dir)
        return content, target_dir

    logger.exit("save_section", return_value=None)

import re
from pathlib import Path

from src.file_manager import create_theme_directory
from src.logger import ProjectLogger

SECTION_PATTERN = re.compile(r"```(\w+)\s*\n(.*?)```", re.DOTALL)
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


def extract_section(text: str, wanted_section_name) -> dict[str, str]:
    logger.entry("extract_section", text=text, wanted_section_name=wanted_section_name)
    wanted_section_name = _normalize_section_name(wanted_section_name)
    sections: dict[str, str] = {}
    for match in SECTION_PATTERN.findall(text):
        found_name = match[0].strip().lower()
        if found_name == wanted_section_name and found_name not in sections:
            sections[found_name] = match[1].strip()
    logger.exit("extract_section", sections=sections)
    return sections


def save_section(
    content,
    theme,
    section_name,
    target_dir: Path | None = None,
    *,
    alias=None,
    return_value=True,
):
    logger.entry(
        "save_section",
        content=content,
        theme=theme,
        section_name=section_name,
        target_dir=target_dir,
        alias=alias,
        return_value=return_value,
    )
    section_name_str = _normalize_section_name(section_name)
    sections = extract_section(content, section_name_str)

    if not sections:
        error_message = "No challenge sections were found in the completion output."
        raise SystemExit(error_message)

    target_dir = target_dir or create_theme_directory(theme, alias)

    section_content = sections.get(section_name_str, "")
    file_path = target_dir / section_name_str
    text_to_write = f"{section_content}\n" if section_content else ""
    file_path.write_text(text_to_write, encoding="utf-8")

    if return_value:
        logger.exit("save_section", section_content=section_content, target_dir=target_dir)
        return section_content, target_dir

    logger.exit("save_section", return_value=None)

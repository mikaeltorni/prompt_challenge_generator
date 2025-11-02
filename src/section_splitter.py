import re
import sys
from pathlib import Path

from src.file_manager import create_theme_directory

SECTION_PATTERN = re.compile(r"```(\w+)\s*\n(.*?)```", re.DOTALL)

def _normalize_section_names(section_names) -> tuple[str, ...]:
	if isinstance(section_names, str):
		return (section_names,)
	return tuple(section_names)

def extract_sections(text: str, section_names) -> dict[str, str]:
	section_names = _normalize_section_names(section_names)
	sections: dict[str, str] = {}
	for match in SECTION_PATTERN.findall(text):
		section_name = match[0].strip().lower()
		if section_name in section_names and section_name not in sections:
			sections[section_name] = match[1].strip()
	return sections

def save_sections(content, theme, section_names, to_return, target_dir: Path | None = None):
	section_names = _normalize_section_names(section_names)
	sections = extract_sections(content, section_names)

	if not sections:
		print("No challenge sections were found in the completion output.", file=sys.stderr)
		raise SystemExit(0)

	target_dir = target_dir or create_theme_directory(theme)

	for section_name in section_names:
		section_content = sections.get(section_name, "")
		if not section_content:
			print(
				f"Section `{section_name}` missing from completion; creating empty file.",
				file=sys.stderr,
			)
		file_path = target_dir / section_name
		text_to_write = f"{section_content}\n" if section_content else ""
		file_path.write_text(text_to_write, encoding="utf-8")

	# Returning the problem statement for the testcase generation
	return sections.get(to_return, ""), target_dir

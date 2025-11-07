import re
import sys
from pathlib import Path

from src.file_manager import create_theme_directory

SECTION_PATTERN = re.compile(r"```(\w+)\s*\n(.*?)```", re.DOTALL)

def _normalize_section_name(section_name) -> str:
	if isinstance(section_name, str):
		return section_name.strip().lower()
	# If it's tuple/list/other, just use first, fallback to str(section_name)
	if isinstance(section_name, (tuple, list)) and section_name:
		return str(section_name[0]).strip().lower()
	return str(section_name).strip().lower()

def extract_section(text: str, wanted_section_name) -> dict[str, str]:
	wanted_section_name = _normalize_section_name(wanted_section_name)
	sections: dict[str, str] = {}
	for match in SECTION_PATTERN.findall(text):
		found_name = match[0].strip().lower()
		if found_name == wanted_section_name and found_name not in sections:
			sections[found_name] = match[1].strip()
	return sections

def save_section(content, theme, section_name, target_dir: Path | None = None, *, alias=None, return_value=True):
	section_name_str = _normalize_section_name(section_name)
	sections = extract_section(content, section_name_str)

	if not sections:
		print("No challenge sections were found in the completion output.", file=sys.stderr)
		raise SystemExit(0)

	target_dir = target_dir or create_theme_directory(theme, alias)

	section_content = sections.get(section_name_str, "")
	if not section_content:
		print(
			f"Section `{section_name_str}` missing from completion; creating empty file.",
			file=sys.stderr,
		)
	file_path = target_dir / section_name_str
	text_to_write = f"{section_content}\n" if section_content else ""
	file_path.write_text(text_to_write, encoding="utf-8")

	# Returning the problem statement for the testcase generation
	if return_value:
		return section_content, target_dir

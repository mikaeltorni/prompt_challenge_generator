import re
import sys
from pathlib import Path

SECTION_PATTERN = re.compile(r"```(\w+)\s*\n(.*?)```", re.DOTALL)

base_dir = Path("generated_challenges")

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

def sanitize_theme(value: str) -> str:
  slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
  return slug or "challenge"

def save_sections(content, theme, section_names, to_return):
    section_names = _normalize_section_names(section_names)
    sections = extract_sections(content, section_names)

    if not sections:
        print("No challenge sections were found in the completion output.", file=sys.stderr)
        raise SystemExit(0)
    
    base_dir.mkdir(exist_ok=True)

    theme_slug = sanitize_theme(theme)
    pattern = re.compile(rf"{re.escape(theme_slug)}-(\d{{3}})$")
    existing_indices = [
    int(match.group(1))
    for entry in base_dir.iterdir()
      if entry.is_dir() and (match := pattern.fullmatch(entry.name))
    ]
    next_index = max(existing_indices, default=0) + 1
    target_dir = base_dir / f"{theme_slug}-{next_index:03d}"
    target_dir.mkdir()

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
    return sections.get(to_return, "")

import re
from pathlib import Path

base_dir = Path("generated_challenges")

def sanitize_theme(value: str) -> str:
	slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
	return slug or "challenge"

def create_theme_directory(theme):
	base_dir.mkdir(parents=True, exist_ok=True)

	theme_slug = sanitize_theme(theme)
	pattern = re.compile(rf"{re.escape(theme_slug)}-(\d{{3}})$")
	existing_indices = [
		int(match.group(1))
		for entry in base_dir.iterdir()
		if entry.is_dir() and (match := pattern.fullmatch(entry.name))
	]
	next_index = max(existing_indices, default=0) + 1
	target_dir = base_dir / f"{theme_slug}-{next_index:03d}"
	target_dir.mkdir(parents=True, exist_ok=False)

	return target_dir

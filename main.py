import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

SECTION_NAMES = ("problem_statement", "examples", "parameter")
SECTION_PATTERN = re.compile(r"```(\w+)\s*\n(.*?)```", re.DOTALL)


def extract_sections(text: str) -> dict[str, str]:
  sections: dict[str, str] = {}
  for match in SECTION_PATTERN.findall(text):
    section_name = match[0].strip().lower()
    if section_name in SECTION_NAMES and section_name not in sections:
      sections[section_name] = match[1].strip()
  return sections


def sanitize_theme(value: str) -> str:
  slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
  return slug or "challenge"

# Load environment variables from a local .env file if present.
load_dotenv(dotenv_path=Path(".env"), override=False)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
  raise RuntimeError(
    "OPENROUTER_API_KEY is missing. Add it to your environment or .env file."
  )

parser = argparse.ArgumentParser(
  description="Generate a prompting challenge problem statement for a given theme."
)
parser.add_argument(
  "--theme",
  required=True,
  help="Theme to focus the prompting challenge around."
)
args = parser.parse_args()

theme = args.theme.strip()
if not theme:
  raise ValueError("Theme cannot be empty.")

# Read the shared system prompt template from prompts/challenge_system_prompt
prompt_file = Path(__file__).parent / "prompts" / "challenge_system_prompt.md"
if not prompt_file.is_file():
  raise FileNotFoundError(
    f"System prompt template not found at {prompt_file}. Create the file to continue."
  )

system_prompt = prompt_file.read_text(encoding="utf-8").strip()
if not system_prompt:
  raise ValueError("System prompt template cannot be empty.")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

completion = client.chat.completions.create(
  model="openai/gpt-5-nano",
  messages=[
    {
      "role": "system",
      "content": system_prompt,
    },
    {
      "role": "user",
      "content": f"{theme}",
    },
  ],
)

message = completion.choices[0].message
content = getattr(message, "content", "") if message else ""

if content is None:
  content = ""

print(content)

sections = extract_sections(content)

if not sections:
  print("No challenge sections were found in the completion output.", file=sys.stderr)
  raise SystemExit(0)

base_dir = Path(__file__).parent / "generated_challenges"
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

for section_name in SECTION_NAMES:
  section_content = sections.get(section_name, "")
  if not section_content:
    print(
      f"Section `{section_name}` missing from completion; creating empty file.",
      file=sys.stderr,
    )
  file_path = target_dir / section_name
  text_to_write = f"{section_content}\n" if section_content else ""
  file_path.write_text(text_to_write, encoding="utf-8")

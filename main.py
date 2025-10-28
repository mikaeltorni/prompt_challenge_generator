import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

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

# Read the shared system prompt template from prompts/challenge_system_prompt.txt.
prompt_file = Path(__file__).parent / "prompts" / "challenge_system_prompt.txt"
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
      "content": f"Theme: {theme}\nGenerate the problem statement now.",
    },
  ],
)

print(completion.choices[0].message.content)

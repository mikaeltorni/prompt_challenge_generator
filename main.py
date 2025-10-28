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

system_prompt = (
  "You design prompt-engineering challenges. Craft a single problem statement for a "
  "prompting challenge. Keep it professional and concise while still inspiring. "
  "Always include three labeled sections: Context, Objective, Success Criteria."
)

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

print(completion.choices[0].message.content)

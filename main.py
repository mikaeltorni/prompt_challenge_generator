import argparse
import os
import re

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

from src.Agent import Agent
from src.section_splitter import save_sections

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

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

#Creation of the challenge generation agent
agent = Agent(client, "openai/gpt-5-nano", "challenge_system_prompt.md")
content = agent.send_message(theme)
print(content)

save_sections(content, theme)

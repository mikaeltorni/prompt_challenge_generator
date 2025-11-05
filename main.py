from itertools import filterfalse
import os

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

from src.Agent import Agent
from src.section_splitter import save_sections
from src.test_cast_writer import generate_promptfoo_test_cases
from src.Args import Args

args = Args()

# Load environment variables from a local .env file if present.
load_dotenv(dotenv_path=Path(".env"), override=False)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
  raise RuntimeError(
    "OPENROUTER_API_KEY is missing. Add it to your environment or .env file."
  )

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

# Creation of the challenge generation agent
challenge_generation_agent = Agent(client, "openai/gpt-5-nano", "problem_statement_system_prompt.md")
content = challenge_generation_agent.send_message(args.theme)
# print(content)

# Saving the sections and we need to return the problem statement for the testcase generation
problem_statement, challenge_dir = save_sections(
  content,
  args.theme,
  ("problem_statement", "examples", "parameter"),
  "problem_statement",
)

#print("pb: ", problem_statement)

test_case_generation_agent = Agent(client, "openai/gpt-5-nano", "test_case_system_prompt.md")
test_case_content = test_case_generation_agent.send_message("Produce exactly " + str(args.test_case_count) + " test cases with the following problem statement:\n" + problem_statement)
#print("test case content: ", test_case_content)

test_cases_split, _ = save_sections(
  test_case_content,
  args.theme,
  ("test_cases"),
  "test_cases",
  target_dir=challenge_dir,
)
print("test cases split: ", test_cases_split)

generate_promptfoo_test_cases(challenge_dir)

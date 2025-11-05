from src.Agent import Agent
from src.section_splitter import save_sections
from src.test_cast_writer import generate_promptfoo_test_cases
from src.Args import Args
from src.ClientConfig import ClientConfig

args = Args()
client = ClientConfig()

# Creation of the challenge generation agent
challenge_generation_agent = Agent(client, "openai/gpt-5-nano", "problem_statement_system_prompt.md")
content = challenge_generation_agent.send_message(args.theme)

# Saving the sections and we need to return the problem statement for the testcase generation
problem_statement, challenge_dir = save_sections(
  content,
  args.theme,
  ("problem_statement", "examples", "parameter"),
  "problem_statement",
)

test_case_generation_agent = Agent(client, "openai/gpt-5-nano", "test_case_system_prompt.md")
test_case_content = test_case_generation_agent.send_message("Produce exactly " + str(args.test_case_count) + " test cases with the following problem statement:\n" + problem_statement)

test_cases_split, _ = save_sections(
  test_case_content,
  args.theme,
  ("test_cases"),
  "test_cases",
  target_dir=challenge_dir,
)
#print("test cases split: ", test_cases_split)

generate_promptfoo_test_cases(challenge_dir)

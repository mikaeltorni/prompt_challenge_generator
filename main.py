from src.Agent import Agent
from src.section_splitter import save_sections
from src.test_cast_writer import generate_promptfoo_test_cases
from src.Args import Args
from src.AgentConfig import AgentConfig
from src.ClientConfig import ClientConfig

client = ClientConfig()
agent_config = AgentConfig(client)
args = Args()

content = agent_config.challenge_generator.send_message(args.theme)

# Saving the sections and we need to return the problem statement for the testcase generation
problem_statement, challenge_dir = save_sections(
  content,
  args.theme,
  ("problem_statement", "examples", "parameter"),
  "problem_statement",
)

test_case_content = agent_config.test_case_generator.send_message("Produce exactly " + str(args.test_case_count) + " test cases with the following problem statement:\n" + problem_statement)

test_cases_split, _ = save_sections(
  test_case_content,
  args.theme,
  ("test_cases"),
  "test_cases",
  target_dir=challenge_dir,
)

generate_promptfoo_test_cases(challenge_dir)

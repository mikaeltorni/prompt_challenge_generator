from src.section_splitter import save_section
from src.test_cast_writer import generate_promptfoo_test_cases
from src.Args import Args
from src.AgentConfig import AgentConfig
from src.ClientConfig import ClientConfig

client = ClientConfig()
agent_config = AgentConfig(client)
args = Args()

problem_statement_content = agent_config.problem_statement_generator.send_message(args.theme)

problem_statement, challenge_dir = save_section(
  problem_statement_content,
  args.theme,
  "problem_statement",
)

### insert these in a multithreading processing since the data is received from the prompt statement

examples_content = agent_config.example_generator.send_message(problem_statement_content)
examples_split, _ = save_section(
  examples_content,
  args.theme,
  "examples",
  target_dir=challenge_dir,
)

parameter_content = agent_config.parameter_generator.send_message(problem_statement_content)
parameters_split, _ = save_section(
  parameter_content,
  args.theme,
  "parameter",
  target_dir=challenge_dir,
)

test_case_content = agent_config.test_case_generator.send_message("Produce exactly " + str(args.test_case_count) + " test cases with the following problem statement:\n" + problem_statement)

test_cases_split, _ = save_section(
  test_case_content,
  args.theme,
  "test_cases",
  target_dir=challenge_dir,
)
###################################################################################################

generate_promptfoo_test_cases(challenge_dir)

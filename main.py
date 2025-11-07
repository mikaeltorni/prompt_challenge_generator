from src.section_splitter import save_section
from src.test_cast_writer import generate_promptfoo_test_cases
from src.Args import Args
from src.AgentConfig import AgentConfig
from src.ClientConfig import ClientConfig

import concurrent.futures

client = ClientConfig()
agent_config = AgentConfig(client)
args = Args()

problem_statement_content = agent_config.problem_statement_generator.send_message(args.theme)

problem_statement, challenge_dir = save_section(
  problem_statement_content,
  args.theme,
  "problem_statement",
  alias=args.alias,
)

# Running these simultaneously since they all get the data from the problem statement generation
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_examples = executor.submit(agent_config.example_generator.send_message, problem_statement_content)
    future_parameter = executor.submit(agent_config.parameter_generator.send_message, problem_statement_content)
    future_test_cases = executor.submit(
        agent_config.test_case_generator.send_message,
        "Produce exactly " + str(args.test_case_count) + " test cases with the following problem statement:\n" + problem_statement
    )

    examples_content = future_examples.result()
    parameter_content = future_parameter.result()
    test_case_content = future_test_cases.result()

# Could save these with one function call from this file
save_section(
  examples_content,
  args.theme,
  "examples",
  target_dir=challenge_dir,
)
save_section(
  parameter_content,
  args.theme,
  "parameter",
  target_dir=challenge_dir,
)
save_section(
  test_case_content,
  args.theme,
  "test_cases",
  target_dir=challenge_dir,
)

generate_promptfoo_test_cases(challenge_dir)

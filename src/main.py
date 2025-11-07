from src.Agent import Agent
from src.section_splitter import save_section
from src.test_cast_writer import generate_promptfoo_test_cases
from src.Args import Args
from src.ClientConfig import ClientConfig
from src.logger import ProjectLogger, reset_iteration, run_with_iteration, set_iteration

logger = ProjectLogger("src/main.py")


def main():
    iteration_token = set_iteration(1)
    logger.entry("main")
    try:
        args = Args()
        client = ClientConfig()

        challenge_generation_agent = Agent(
            client,
            "Challenge Generator",
            "openai/gpt-5-nano",
            "problem_statement_system_prompt.md",
        )
        content = challenge_generation_agent.send_message(args.theme)

        problem_statement, challenge_dir = save_section(
            content,
            args.theme,
            "problem_statement",
            alias=args.alias,
            iteration=1,
        )
        save_section(
            content,
            args.theme,
            "examples",
            target_dir=challenge_dir,
        )
        save_section(
            content,
            args.theme,
            "parameter",
            target_dir=challenge_dir,
        )

        test_case_generation_agent = Agent(
            client,
            "Test Case Generator",
            "openai/gpt-5-nano",
            "test_case_system_prompt.md",
        )
        test_case_content = test_case_generation_agent.send_message(
            "Produce exactly "
            + str(args.test_case_count)
            + " test cases with the following problem statement:\n"
            + problem_statement
        )

        save_section(
            test_case_content,
            args.theme,
            "test_cases",
            target_dir=challenge_dir,
        )

        run_with_iteration(1, generate_promptfoo_test_cases, challenge_dir)
        logger.exit("main", return_value=None)
    finally:
        reset_iteration(iteration_token)


if __name__ == "__main__":
    main()

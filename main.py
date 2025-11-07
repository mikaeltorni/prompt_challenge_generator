import concurrent.futures

from src.section_splitter import save_section
from src.test_cast_writer import generate_promptfoo_test_cases
from src.Args import Args
from src.AgentConfig import AgentConfig
from src.ClientConfig import ClientConfig
from src.logger import (
    ProjectLogger,
    attach_iteration_log,
    detach_iteration_log,
    initialize_iteration_log,
    reset_iteration,
    run_with_iteration,
    set_iteration,
)
from src.file_manager import next_iteration_numbers

logger = ProjectLogger("main.py")

args = Args()
client = ClientConfig()
agent_config = AgentConfig(client)
iteration_assignments: dict[int, int] = {}


def _generate_single_challenge(run_number: int):
    iteration_value = iteration_assignments[run_number]
    iteration_token = set_iteration(iteration_value)
    initialize_iteration_log(iteration_value)
    logger.entry("_generate_single_challenge", run_number=run_number, iteration=iteration_value)
    try:
        problem_statement_content = agent_config.problem_statement_generator.send_message(args.theme)

        problem_statement, challenge_dir = save_section(
            problem_statement_content,
            args.theme,
            "problem_statement",
            alias=args.alias,
            iteration=iteration_value,
        )
        attach_iteration_log(iteration_value, challenge_dir)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_examples = executor.submit(
                run_with_iteration,
                iteration_value,
                agent_config.example_generator.send_message,
                problem_statement_content,
            )
            future_parameter = executor.submit(
                run_with_iteration,
                iteration_value,
                agent_config.parameter_generator.send_message,
                problem_statement_content,
            )
            future_test_cases = executor.submit(
                run_with_iteration,
                iteration_value,
                agent_config.test_case_generator.send_message,
                "Produce exactly "
                + str(args.test_case_count)
                + " test cases with the following problem statement:\n"
                + problem_statement,
            )

            examples_content = future_examples.result()
            parameter_content = future_parameter.result()
            test_case_content = future_test_cases.result()

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
        logger.exit("_generate_single_challenge", return_value=None)
    finally:
        detach_iteration_log(iteration_value)
        reset_iteration(iteration_token)


def main():
    logger.entry("main")
    iteration_values = next_iteration_numbers(args.theme, args.alias, args.n)
    global iteration_assignments
    iteration_assignments = {
        run_index + 1: iteration
        for run_index, iteration in enumerate(iteration_values)
    }
    if args.n == 1:
        _generate_single_challenge(1)
        logger.exit("main", return_value=None)
        return

    max_workers = min(args.max_concurrent, args.n)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_generate_single_challenge, run_index + 1): run_index + 1
            for run_index in range(args.n)
        }
        for future in concurrent.futures.as_completed(futures):
            run_number = futures[future]
            future.result()

    logger.exit("main", return_value=None)


if __name__ == "__main__":
    main()

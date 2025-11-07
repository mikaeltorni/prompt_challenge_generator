from src.Agent import Agent
from src.logger import ProjectLogger

logger = ProjectLogger("AgentConfig.py")


class AgentConfig:
    def __init__(self, client):
        logger.entry("__init__", client=client)
        self.problem_statement_generator = Agent(
            client,
            "Challenge Generator",
            "openai/gpt-5-nano",
            "problem_statement_system_prompt.md",
        )
        self.example_generator = Agent(
            client,
            "Example Generator",
            "openai/gpt-5-nano",
            "example_system_prompt.md",
        )
        self.parameter_generator = Agent(
            client,
            "Parameter Generator",
            "openai/gpt-5-nano",
            "parameter_system_prompt.md",
        )
        self.test_case_generator = Agent(
            client,
            "Test Case Generator",
            "openai/gpt-5-nano",
            "test_case_system_prompt.md",
            max_tokens=128000,
        )
        logger.exit("__init__", return_value=None)

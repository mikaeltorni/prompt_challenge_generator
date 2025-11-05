from src.Agent import Agent

class AgentConfig:
    def __init__(self, client):
        self.challenge_generator = Agent(client, "openai/gpt-5-nano", "problem_statement_system_prompt.md")
        self.test_case_generator = Agent(client, "openai/gpt-5-nano", "test_case_system_prompt.md")

from src.logger import ProjectLogger

module_logger = ProjectLogger("Agent.py")


class Agent:
    def __init__(self, client, agent_name, model, system_prompt_name, temperature = 0, max_tokens = 16384):
        agent_logger = module_logger.with_agent(agent_name)
        agent_logger.entry(
            "__init__",
            client=client,
            agent_name=agent_name,
            model=model,
            system_prompt_name=system_prompt_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        self.client = client
        self.agent_name = agent_name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = agent_logger

        self.system_prompt = self.get_system_prompt(system_prompt_name)
        self.logger.exit("__init__", return_value=None)

    def get_system_prompt(self, system_prompt_name):
        self.logger.entry("get_system_prompt", system_prompt_name=system_prompt_name)
        prompt_file = "prompts/" + system_prompt_name
        prompt_content = open(prompt_file, "r").read()
        self.logger.exit("get_system_prompt", prompt_content=prompt_content)
        return prompt_content

    def send_message(self, input):
        self.logger.entry("send_message", input=input)

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": input,
                },
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        message = completion.choices[0].message
        content = getattr(message, "content", "") if message else ""

        if content is None:
            content = ""

        self.logger.exit("send_message", content=content)
        return content

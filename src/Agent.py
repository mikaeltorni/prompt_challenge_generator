class Agent:
    def __init__(self, client, agent_name, model, system_prompt_name, temperature = 0, max_tokens = 16384):
        print("Initiating Agent: " + agent_name + " with model: " + model + " with parameters of temp: " + str(temperature) + " and max_tokens: " + str(max_tokens))

        self.client = client
        self.agent_name = agent_name
        self.model = model
        self.system_prompt = self.get_system_prompt(system_prompt_name)

        self.temperature = temperature
        self.max_tokens = max_tokens

    def get_system_prompt(self, system_prompt_name):
        prompt_file = "prompts/" + system_prompt_name
        return open(prompt_file, "r").read()

    def send_message(self, input):
        print("Agent + " + self.agent_name + " received input: " + input)

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
            print("No content was returned from the agent")
            content = ""

        print("Agent + " + self.agent_name + " msg sending complete with " + content)

        u = getattr(completion, "usage", None)
        if u:
            completion_tokens = getattr(u, "completion_tokens", None) or u.get("completion_tokens")
            print(f"Agent + {self.agent_name} completion tokens={completion_tokens}")

        return content
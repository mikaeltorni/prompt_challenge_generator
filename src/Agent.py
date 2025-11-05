class Agent:
    def __init__(self, client, model, system_prompt_name, temperature = 0, max_tokens = 16384):
        self.client = client
        self.model = model
        self.system_prompt = self.get_system_prompt(system_prompt_name)

        self.temperature = temperature
        self.max_tokens = max_tokens

    def get_system_prompt(self, system_prompt_name):
        prompt_file = "prompts/" + system_prompt_name
        return open(prompt_file, "r").read()

    def send_message(self, input):
        print("Agent received input: " + input)

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

        print("msg sending complete with " + content)

        u = getattr(completion, "usage", None)
        if u:
            completion_tokens = getattr(u, "completion_tokens", None) or u.get("completion_tokens")
            print(f"completion tokens={completion_tokens}")

        return content
class Agent:
    def __init__(self, client, model, system_prompt_name):
        self.client = client
        #could add parameters class here instead of the model
        self.model = model
        self.system_prompt = self.get_system_prompt(system_prompt_name)

    def get_system_prompt(self, system_prompt_name):
        prompt_file = "prompts/" + system_prompt_name
        return open(prompt_file, "r").read()
    
    def send_message(self, input):
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=[
                {
                "role": "system",
                "content": self.system_prompt,
                },
                {
                "role": "user",
                "content": "input",
                },
            ],
        )

        message = completion.choices[0].message
        content = getattr(message, "content", "") if message else ""

        if content is None:
            print("No content was returned from the agent")
            content = ""

        return content
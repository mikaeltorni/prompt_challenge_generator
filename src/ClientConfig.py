import os

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

class ClientConfig(OpenAI):
    def __init__(self):
        load_dotenv(dotenv_path=Path(".env"), override=False)

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is missing. Add it to your environment or .env file."
            )

        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

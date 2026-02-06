import requests
import re
import logging

logger = logging.getLogger(__name__)


class LocalLLM:
    """
    Local LLM wrapper using Ollama.
    Sends a prompt and returns generated SQL.
    """

    def __init__(self, model_name: str = "qwen2.5-coder:7b"):
        self.model = model_name
        self.base_url = "http://localhost:11434"

        logger.info(f"[LLM] Using Ollama model: {self.model}")

    def _clean_sql(self, text: str) -> str:
        # remove markdown fences
        text = text.replace("```sql", "").replace("```", "")

        # find first SQL statement ending with ;
        match = re.search(r"(SELECT[\s\S]*?;)", text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return text.strip()

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.0,
                    "repeat_penalty": 1.05,
                },
            },
        )

        response.raise_for_status()
        generated = response.json()["response"].strip()

        return self._clean_sql(generated)

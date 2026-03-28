import os
import re
import logging
from groq import Groq

logger = logging.getLogger(__name__)


class LocalLLM:
    """
    LLM wrapper using Groq API for fast cloud inference.
    Sends a prompt and returns generated SQL.
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model = model_name
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        logger.info(f"[LLM] Using Groq model: {self.model}")

    def _clean_sql(self, text: str) -> str:
        # remove markdown fences
        text = text.replace("```sql", "").replace("```", "")

        # find first SQL statement ending with ;
        match = re.search(r"(SELECT[\s\S]*?;)", text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return text.strip()

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=max_tokens,
        )

        generated = response.choices[0].message.content.strip()

        return self._clean_sql(generated)

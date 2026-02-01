import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import re

class LocalLLM:
    """
    Minimal local LLM wrapper.
    Takes a prompt and returns generated SQL text only.
    """

    def __init__(
        self,
        model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        device: str | None = None
    ):
        # auto choose GPU if available
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = device

        print(f"[LLM] Loading {model_name} on {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto"
        )

        self.model.eval()

    # remove markdown / explanations
    

    def _clean_sql(self, text: str) -> str:
        # remove markdown fences
        text = text.replace("```sql", "").replace("```", "")

        # find first SQL statement ending with ;
        match = re.search(r"(SELECT[\s\S]*?;)", text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return text.strip()


    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.0,   # deterministic
                do_sample=False,
                repetition_penalty=1.05,
                pad_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        generated = decoded[len(prompt):].strip()

        return self._clean_sql(generated)

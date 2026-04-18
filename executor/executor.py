import os
from typing import List, Dict

from executor.prompt_builder import PromptBuilder
from utils.rate_limiter import RateLimiter

from dotenv import load_dotenv
load_dotenv()


class Executor:
    def __init__(self, use_llm: bool = False, provider: str = "groq", debug: bool = False):
        """
        Executor:
        → Calls LLM safely
        → Enforces rate limiting
        → Prevents output explosion
        """

        self.use_llm = use_llm
        self.provider = provider
        self.prompt_builder = PromptBuilder()
        self.debug = debug

        self.rate_limiter = RateLimiter(max_calls=25, period=60)

    def run(self, context: List[Dict], task: str) -> List[Dict]:
        prompt = self.prompt_builder.build_prompt(context, task)

        if self.debug:
            print("\n🧠 PROMPT:\n", prompt[:500])

        if self.use_llm:
            response = self._call_llm(prompt)
        else:
            response = self._mock_llm()

        return [{"suggestion": response}]

    def _mock_llm(self) -> str:
        return "FILE: main.py\ndef run():\n    pass"

    def _call_llm(self, prompt: str) -> str:
        if not self.rate_limiter.allow():
            raise Exception("🚫 Rate limit exceeded")

        if self.provider == "groq":
            return self._call_groq(prompt)

        raise ValueError("Unsupported provider")

    def _call_groq(self, prompt: str) -> str:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY")

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,   # deterministic
            top_p=1.0,
            max_tokens=500     # 🔥 prevent explosion
        )

        output = response.choices[0].message.content.strip()

        # 🚨 EXPLOSION GUARD
        if output.count("FILE:") > 10:
            raise Exception("🚫 LLM output explosion detected")

        return output
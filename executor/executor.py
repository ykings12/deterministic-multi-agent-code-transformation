import os
from typing import List, Dict

from executor.prompt_builder import PromptBuilder
from utils.rate_limiter import RateLimiter

from dotenv import load_dotenv
load_dotenv()


class Executor:
    def __init__(self, use_llm: bool = False, provider: str = "groq", debug: bool = False):
        """
        Executor runs LLM to generate code improvements.

        Features:
        → Provider-agnostic
        → Rate-limited
        → Debug-controlled logging
        """

        self.use_llm = use_llm
        self.provider = provider
        self.debug = debug
        self.prompt_builder = PromptBuilder()

        # Rate limiter: 25 calls per minute
        self.rate_limiter = RateLimiter(max_calls=25, period=60)

    def run(self, context: List[Dict], task: str) -> List[Dict]:
        """
        Main execution function
        """

        prompt = self.prompt_builder.build_prompt(context, task)

        # ✅ Debug logging only
        if self.debug:
            print("\n🧠 PROMPT SENT TO LLM:\n")
            print(prompt[:500])
            print("\n" + "-" * 60)

        if self.use_llm:
            response = self._call_llm(prompt)
        else:
            response = self._mock_llm()

        return [{"suggestion": response}]

    def _mock_llm(self) -> str:
        if self.debug:
            print("⚠️ Using MOCK LLM")
        return "Mocked improvement: Optimize functions"

    def _call_llm(self, prompt: str) -> str:
        """
        Generic LLM caller with rate limiting
        """

        if not self.rate_limiter.allow():
            raise Exception("🚫 Rate limit exceeded. Try again later.")

        if self.debug:
            print(f"🚀 Calling REAL LLM using provider: {self.provider}")

        if self.provider == "groq":
            return self._call_groq_provider(prompt)

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _call_groq_provider(self, prompt: str) -> str:
        """
        Groq API call
        """

        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found in environment")

        client = Groq(api_key=api_key)

        if self.debug:
            print("📡 Sending request to Groq API...")

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,   # deterministic
            top_p=1.0,
            max_tokens=800     # reduced for tighter output
        )

        if self.debug:
            print("✅ Response received")

        return response.choices[0].message.content.strip()
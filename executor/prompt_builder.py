from typing import List, Dict


class PromptBuilder:
    def build_prompt(self, context: List[Dict], task: str) -> str:
        """
        Builds a STRICT, schema-driven prompt for deterministic LLM output.

        GOAL:
        → Convert LLM from "assistant" → "code transformation engine"
        """

        prompt = ""

        # -----------------------------
        # ROLE DEFINITION (STRICT)
        # -----------------------------
        prompt += "You are a deterministic code transformation engine.\n"
        prompt += "You DO NOT explain.\n"
        prompt += "You DO NOT add comments.\n"
        prompt += "You DO NOT output markdown.\n"
        prompt += "You ONLY output raw Python code.\n\n"

        # -----------------------------
        # TASK
        # -----------------------------
        prompt += f"TASK:\n{task}\n\n"

        # -----------------------------
        # CONTEXT
        # -----------------------------
        prompt += "INPUT CODEBASE:\n"

        for item in context:
            prompt += f"\nFILE: {item['file']}\n"
            prompt += item["code"] + "\n"

        # -----------------------------
        # STRICT OUTPUT CONTRACT
        # -----------------------------
        prompt += "\nOUTPUT FORMAT (MANDATORY):\n"
        prompt += "For each modified file, output EXACTLY:\n\n"

        prompt += "FILE: <filename>\n"
        prompt += "<complete modified code>\n\n"

        prompt += "RULES:\n"
        prompt += "1. ONLY output files that were modified\n"
        prompt += "2. DO NOT include ``` or markdown\n"
        prompt += "3. DO NOT include explanations\n"
        prompt += "4. DO NOT include headings\n"
        prompt += "5. DO NOT include any text outside the format\n"
        prompt += "6. If no changes needed, output NOTHING\n"

        return prompt
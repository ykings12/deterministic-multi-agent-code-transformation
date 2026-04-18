from typing import List, Dict


class PromptBuilder:
    def build_prompt(self, context: List[Dict], task: str) -> str:
        """
        STRICT prompt for deterministic behavior
        """

        prompt = ""

        # ROLE
        prompt += "You are a deterministic code transformation engine.\n"
        prompt += "You MUST follow all rules strictly.\n"
        prompt += "You DO NOT explain.\n"
        prompt += "You DO NOT add comments.\n"
        prompt += "You DO NOT output markdown.\n\n"

        # TASK
        prompt += f"TASK:\n{task}\n\n"

        # 🔥 CRITICAL CONSTRAINTS
        prompt += "CRITICAL CONSTRAINTS:\n"
        prompt += "- DO NOT change return values\n"
        prompt += "- DO NOT change function behavior\n"
        prompt += "- DO NOT introduce new side effects\n"
        prompt += "- DO NOT add print/logging\n"
        prompt += "- ONLY refactor for readability\n\n"

        # CONTEXT
        prompt += "INPUT CODEBASE:\n"
        for item in context:
            prompt += f"\nFILE: {item['file']}\n{item['code']}\n"

        # OUTPUT FORMAT
        prompt += "\nOUTPUT FORMAT:\n"
        prompt += "FILE: <filename>\n<code>\n\n"

        prompt += "RULES:\n"
        prompt += "1. Only output modified files\n"
        prompt += "2. No extra text\n"
        prompt += "3. No explanations\n"

        return prompt
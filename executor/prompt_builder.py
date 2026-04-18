from typing import List, Dict


class PromptBuilder:
    def build_prompt(self, context: List[Dict], task: str) -> str:
        """
        STRICT deterministic prompt.

        Design Goals:
        → No hallucination
        → No format drift
        → No extra files
        """

        prompt = ""

        # -----------------------------
        # ROLE
        # -----------------------------
        prompt += "You are a deterministic code transformation engine.\n"
        prompt += "You MUST follow ALL rules strictly.\n"
        prompt += "You DO NOT explain.\n"
        prompt += "You DO NOT add comments.\n"
        prompt += "You DO NOT output markdown.\n\n"

        # -----------------------------
        # TASK (includes feedback)
        # -----------------------------
        prompt += f"TASK:\n{task}\n\n"

        # -----------------------------
        # HARD CONSTRAINTS
        # -----------------------------
        prompt += "CRITICAL CONSTRAINTS:\n"
        prompt += "- DO NOT change return values\n"
        prompt += "- DO NOT change function behavior\n"
        prompt += "- DO NOT introduce new side effects\n"
        prompt += "- DO NOT add print/logging\n"
        prompt += "- DO NOT introduce new functions\n"
        prompt += "- DO NOT change file structure\n"
        prompt += "- ONLY refactor for readability\n\n"

        # -----------------------------
        # FILE CONSTRAINTS
        # -----------------------------
        prompt += "STRICT FILE CONSTRAINT:\n"
        prompt += "You are ONLY allowed to modify these files:\n"

        for item in context:
            prompt += f"- {item['file']}\n"

        prompt += "\nDO NOT create or modify ANY other files.\n"
        prompt += "Each file must appear ONLY ONCE in output.\n"
        prompt += "Duplicate files = INVALID OUTPUT.\n\n"

        # -----------------------------
        # INPUT CONTEXT
        # -----------------------------
        prompt += "INPUT CODEBASE:\n"

        for item in context:
            prompt += f"\nFILE: {item['file']}\n"
            prompt += item["code"] + "\n"

        # -----------------------------
        # OUTPUT FORMAT
        # -----------------------------
        prompt += "\nOUTPUT FORMAT (MANDATORY):\n"
        prompt += "FILE: <filename>\n"
        prompt += "<complete modified code>\n\n"

        prompt += "RULES:\n"
        prompt += "1. Only output modified files\n"
        prompt += "2. No explanations\n"
        prompt += "3. No markdown\n"
        prompt += "4. No extra text\n"

        return prompt
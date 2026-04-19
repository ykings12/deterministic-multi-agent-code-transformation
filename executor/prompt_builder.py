from typing import List, Dict


class PromptBuilder:
    def build_prompt(self, context: List[Dict], task: str) -> str:
        """
        ULTRA-STRICT deterministic prompt.

        GOAL:
        → Force LLM to behave like a compiler, not a developer
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
        # TASK
        # -----------------------------
        prompt += f"TASK:\n{task}\n\n"

        # -----------------------------
        # 🔥 CRITICAL SAFETY RULES
        # -----------------------------
        prompt += "CRITICAL RULES (HIGHEST PRIORITY):\n"
        prompt += "- If NO safe refactor is possible → OUTPUT NOTHING\n"
        prompt += "- Prefer NO change over risky change\n"
        prompt += "- DO NOT rewrite full functions\n"
        prompt += "- DO NOT rename functions\n"
        prompt += "- DO NOT introduce new variables unless necessary\n\n"

        # -----------------------------
        # HARD CONSTRAINTS
        # -----------------------------
        prompt += "CONSTRAINTS:\n"
        prompt += "- DO NOT change return values\n"
        prompt += "- DO NOT change function behavior\n"
        prompt += "- DO NOT introduce new side effects\n"
        prompt += "- DO NOT add print/logging\n"
        prompt += "- DO NOT introduce new functions\n"
        prompt += "- DO NOT change file structure\n"
        prompt += "- ONLY minimal readability improvements allowed\n\n"

        # -----------------------------
        # FILE CONSTRAINTS
        # -----------------------------
        prompt += "STRICT FILE CONSTRAINT:\n"
        prompt += "You are ONLY allowed to modify these files:\n"

        for item in context:
            prompt += f"- {item['file']}\n"

        prompt += "\nDO NOT modify any other files.\n"
        prompt += "Each file must appear ONLY ONCE.\n\n"

        # -----------------------------
        # 🔥 VERY IMPORTANT
        # -----------------------------
        prompt += "MODIFICATION STRATEGY:\n"
        prompt += "- Modify ONLY the MOST relevant file\n"
        prompt += "- Avoid modifying dependency/helper files\n"
        prompt += "- Minimal edits ONLY\n\n"

        # -----------------------------
        # INPUT
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
        prompt += "<code>\n\n"

        prompt += "RULES:\n"
        prompt += "1. Output ONLY modified files\n"
        prompt += "2. NO explanations\n"
        prompt += "3. NO markdown\n"
        prompt += "4. NO extra text\n"
        prompt += "5. If no changes → OUTPUT NOTHING\n"

        prompt += "\nFINAL REMINDER:\n"
        prompt += "Every output MUST start with 'FILE: <filename>'\n"
        prompt += "Each file must appear EXACTLY once\n"
        prompt += "No duplicate files\n"

        return prompt
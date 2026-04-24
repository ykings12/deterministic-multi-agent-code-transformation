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

        prompt += "DEFAULT BEHAVIOR:\n"
        prompt += "- Assume NO change is required unless absolutely necessary\n"
        prompt += "- Prefer returning original code\n\n"

        # -----------------------------
        # 🔥 CRITICAL SAFETY RULES
        # -----------------------------
        prompt += "CRITICAL RULES (HIGHEST PRIORITY):\n"
        prompt += "- If NO safe refactor is possible → OUTPUT NOTHING\n"
        prompt += "- Prefer NO change over risky change\n"
        prompt += "- DO NOT rewrite full functions\n"
        prompt += "- DO NOT rename functions\n"
        prompt += "- DO NOT introduce new variables unless necessary\n\n"

        prompt += "- NEVER change string literals (e.g., 'hello' must remain 'hello')\n"
        prompt += "- NEVER change return values\n"
        prompt += "- If a function returns a constant → DO NOT modify it\n"
        prompt += "- DO NOT optimize or improve logic\n"
        prompt += "- DO NOT simplify expressions\n\n"

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
        # 🔥 FUNCTION DETECTION
        # -----------------------------
        has_functions = any(item.get("functions") for item in context)

        if has_functions:
            prompt += "\nIMPORTANT:\n"
            prompt += "This task involves function modification.\n"
            prompt += "You MUST use EDIT format ONLY.\n"
            prompt += "FILE format is STRICTLY FORBIDDEN.\n\n"

        prompt += "\nOUTPUT FORMAT (STRICT):\n"

        if has_functions:
            prompt += "MANDATORY:\n"
            prompt += "- Use ONLY EDIT format\n"
            prompt += "- DO NOT output FILE format\n\n"
        else:
            prompt += "MANDATORY:\n"
            prompt += "- Use FILE format\n\n"

        prompt += "EDIT FORMAT:\n"
        prompt += "EDIT: <filename>\n"
        prompt += "TYPE: replace_function\n"
        prompt += "TARGET: <function_name>\n"
        prompt += "CODE:\n"
        prompt += "<new function code>\n\n"

        prompt += "FILE FORMAT:\n"
        prompt += "FILE: <filename>\n"
        prompt += "<code>\n\n"

        prompt += "CRITICAL RULES:\n"
        prompt += "- NEVER mix FILE and EDIT\n"
        prompt += "- If EDIT is used → NO FILE allowed\n"
        prompt += "- If you include FILE with EDIT → OUTPUT IS INVALID\n"
        prompt += "- If unsure → OUTPUT NOTHING\n"

        return prompt

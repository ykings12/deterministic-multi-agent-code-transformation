import os
from typing import Dict


class FileEditor:
    def __init__(self, repo_path: str):
        """
        FileEditor applies LLM changes to actual files.

        WHY?
        → Bridge between AI suggestions and real codebase
        """

        self.repo_path = repo_path

    def apply_changes(self, llm_output: str):
        """
        Main function:
        - Parse LLM output
        - Write changes to files
        """

        files = self._parse_output(llm_output)

        for file_name, code in files.items():
            full_path = os.path.join(self.repo_path, file_name)

            print(f"✏️ Writing changes to: {file_name}")

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(code.strip() + "\n")

    # -----------------------------
    # PARSER (same logic as reviewer)
    # -----------------------------
    def _parse_output(self, output: str) -> Dict[str, str]:
        """
        Parse LLM output → file → code mapping
        """

        files = {}
        current_file = None
        code_lines = []

        for line in output.split("\n"):
            if line.startswith("FILE:"):
                if current_file:
                    files[current_file] = "\n".join(code_lines)

                current_file = line.replace("FILE:", "").strip()
                code_lines = []
            else:
                code_lines.append(line)

        if current_file:
            files[current_file] = "\n".join(code_lines)

        return files

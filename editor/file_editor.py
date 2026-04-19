import os
from typing import Dict


class FileEditor:
    def __init__(self, repo_path: str):
        """
        Applies LLM-generated changes to actual files.

        WHY?
        → Converts suggestions into real code updates
        """

        self.repo_path = repo_path

    def apply_changes(self, llm_output: str):
        """
        Parse LLM output and write changes to files.
        """

        files = self._parse_output(llm_output)

        for file_name, code in files.items():
            full_path = os.path.join(self.repo_path, file_name)

            if not os.path.exists(full_path):
                print(f"⚠️ Skipping non-existent file: {file_name}")
                continue

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(code.strip() + "\n")

            print(f"💾 Updated: {file_name}")

    def _parse_output(self, output: str) -> Dict[str, str]:
        """
        Convert LLM output → {file: code}
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

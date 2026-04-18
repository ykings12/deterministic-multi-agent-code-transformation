import os
from typing import List, Dict, Any


class ContextBuilder:
    def __init__(self, codebase_map: Dict[str, Any], repo_path: str):
        """
        Context Builder prepares LLM-ready input.

        Inputs:
        - codebase_map → full system understanding
        - repo_path → to read actual files

        WHY separate class?
        → Clean separation between selection and packaging
        """

        self.map = codebase_map
        self.repo_path = repo_path

    def build_context(self, selected_files: List[str]) -> List[Dict]:
        """
        Main function:
        Builds structured context for LLM

        Output format:
        [
            {
                "file": "a.py",
                "code": "...",
                "functions": [...]
            }
        ]

        WHY structured format?
        → LLM understands structured input better
        → Enables precise edits later
        """

        context = []

        for file_path in selected_files:
            full_path = os.path.join(self.repo_path, file_path)

            # Read actual file content
            code = self._read_file(full_path)

            # Extract AST metadata
            ast_data = self.map["ast"].get(file_path, {})

            context.append({
                "file": file_path,
                "code": code,
                "functions": ast_data.get("functions", []),
                "classes": ast_data.get("classes", [])
            })

        return context

    def _read_file(self, file_path: str) -> str:
        """
        Reads file safely.

        WHY separate function?
        → Easier testing
        → Handles errors gracefully
        """

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
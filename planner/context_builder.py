import os
from typing import List, Dict, Any


import os
from typing import List, Dict


class ContextBuilder:
    def __init__(self, codebase_map: Dict, repo_path: str):
        self.map = codebase_map
        self.repo_path = repo_path

    def build_function_context(self, selected_functions: List[Dict]) -> List[Dict]:
        """
        Build context ONLY for selected functions.
        """

        context = []

        for item in selected_functions:
            file_path = os.path.join(self.repo_path, item["file"])

            with open(file_path, "r") as f:
                code = f.read()

            function_code = self._extract_function_code(code, item["function"])

            context.append({
                "file": item["file"],
                "code": function_code,
                "functions": [item["function"]]
            })

        return context

    def _extract_function_code(self, code: str, function_name: str) -> str:
        """
        Naive extraction (can improve later using AST spans)
        """

        lines = code.split("\n")
        capture = False
        result = []

        for line in lines:
            if line.strip().startswith(f"def {function_name}"):
                capture = True

            if capture:
                result.append(line)

                if line.strip() == "":
                    break

        return "\n".join(result)
    
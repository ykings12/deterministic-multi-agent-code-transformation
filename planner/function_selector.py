from typing import List, Dict


class FunctionSelector:
    def __init__(self, codebase_map: Dict):
        """
        Selects MOST relevant functions instead of full files.

        WHY?
        → Reduces LLM context size
        → Improves precision
        """

        self.map = codebase_map

    def select_functions(self, files: List[str], query: str) -> List[Dict]:
        """
        Returns:
        [
            {
                "file": "utils.py",
                "function": "helper",
                "code": "def helper(): ..."
            }
        ]
        """

        selected = []
        keywords = query.lower().split()

        for file in files:
            functions = self.map["ast"].get(file, {}).get("functions", [])

            for func in functions:
                if self._match(func["name"], keywords):
                    selected.append({
                        "file": file,
                        "function": func["name"]
                    })

        return selected

    def _match(self, func_name: str, keywords: List[str]) -> bool:
        return any(kw in func_name.lower() for kw in keywords)
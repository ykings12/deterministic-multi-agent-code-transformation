from typing import List, Dict, Any


class QueryEngine:
    def __init__(self, codebase_map: Dict[str, Any]):
        """
        Improved QueryEngine using:
        - File names
        - AST (functions)
        - Call Graph (relationships)
        - Dependency Graph

        WHY?
        → More intelligent context selection
        """

        self.map = codebase_map

    def query(self, user_query: str, top_k: int = 5) -> List[str]:
        """
        Main function.

        Steps:
        1. Extract keywords
        2. Score files using multiple signals
        3. Return top_k files
        """

        keywords = self._extract_keywords(user_query)

        scores = []

        for file in self.map["files"]:
            file_path = file["path"]

            score = self._compute_score(file, keywords)

            scores.append((file_path, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        # Filter out irrelevant files (score <= 0)
        filtered = [file for file, score in scores if score > 0]

        return filtered[:top_k]

    def _extract_keywords(self, query: str) -> List[str]:
        return query.lower().split()

    def _compute_score(self, file: Dict, keywords: List[str]) -> float:
        """
        Improved scoring:

        score =
            file_name_match +
            function_match +
            call_graph_match +
            dependency_score -
            size_penalty
        """

        file_path = file["path"]

        file_score = self._file_name_match(file_path, keywords)
        function_score = self._function_match(file_path, keywords)
        call_score = self._call_graph_match(file_path, keywords)
        dependency_score = self._dependency_score(file_path)
        size_penalty = file["size"] / 1000

        return file_score + function_score + call_score + dependency_score - size_penalty

    def _file_name_match(self, file_path: str, keywords: List[str]) -> int:
        return sum(1 for kw in keywords if kw in file_path.lower())

    def _function_match(self, file_path: str, keywords: List[str]) -> int:
        """
        Match keywords with function names (AST)
        """
        functions = self.map["ast"].get(file_path, {}).get("functions", [])

        score = 0
        for func in functions:
            for kw in keywords:
                if kw in func["name"].lower():
                    score += 2  # higher weight

        return score

    def _call_graph_match(self, file_path: str, keywords: List[str]) -> int:
        """
        Match based on function calls
        """
        score = 0

        for func_key, calls in self.map["call_graph"].items():
            if func_key.startswith(file_path):
                for call in calls:
                    for kw in keywords:
                        if kw in call.lower():
                            score += 1

        return score

    def _dependency_score(self, file_path: str) -> int:
        deps = self.map["dependencies"].get(file_path, [])
        return len(deps)
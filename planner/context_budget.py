from typing import List, Dict, Any


class ContextBudget:
    def __init__(self, codebase_map: Dict[str, Any]):
        """
        Smart context selector using:
        - File names
        - AST (functions)
        - Call graph
        - Dependencies

        GOAL:
        → Send ONLY relevant files to LLM
        """

        self.map = codebase_map

    def select_top_k(self, query: str, k: int = 3) -> List[str]:
        """
        Select top-k MOST relevant files.

        IMPORTANT:
        → Do NOT blindly expand dependencies (causes explosion)
        """

        keywords = self._extract_keywords(query)

        scored_files = []

        for file in self.map["files"]:
            file_path = file["path"]

            score = self._compute_score(file, keywords)

            scored_files.append((file_path, score))

        # Sort descending
        scored_files.sort(key=lambda x: x[1], reverse=True)

        # ✅ Only pick top-k STRICTLY
        top_files = [file for file, score in scored_files[:k] if score > 0]

        # ✅ LIMITED dependency expansion (controlled)
        expanded = set(top_files)

        for file in top_files:
            deps = self.map.get("dependencies", {}).get(file, [])

            # 🔥 ONLY include 1-level dependencies
            for dep in deps[:1]:  # limit explosion
                expanded.add(dep)

        return list(expanded)

    # -----------------------------
    # SCORING
    # -----------------------------

    def _compute_score(self, file: Dict, keywords: List[str]) -> float:
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
        🔥 AST-based scoring
        """

        functions = self.map["ast"].get(file_path, {}).get("functions", [])

        score = 0

        for func in functions:
            for kw in keywords:
                if kw in func["name"].lower():
                    score += 3  # HIGH weight

        return score

    def _call_graph_match(self, file_path: str, keywords: List[str]) -> int:
        """
        🔥 Call graph scoring
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
        return len(self.map.get("dependencies", {}).get(file_path, []))

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Better keyword extraction
        """

        return [
            word.strip().lower()
            for word in query.split()
            if len(word) > 2  # remove noise like "to", "of"
        ]
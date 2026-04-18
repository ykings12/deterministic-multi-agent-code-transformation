from typing import List, Dict, Any


class ContextBudget:
    def __init__(self, codebase_map: Dict[str, Any]):
        """
        ContextBudget decides WHICH files go to LLM.

        WHY?
        → LLM context is expensive
        → We must send only relevant files

        INPUT:
        codebase_map = {
            "files": [...],
            "dependencies": {...}
        }
        """

        self.map = codebase_map

    def select_top_k(self, query: str, k: int = 3) -> List[str]:
        """
        Select top-k files AND include their dependencies
        """

        keywords = self._extract_keywords(query)

        scored_files = []

        for file in self.map["files"]:
            file_path = file["path"]
            score = self._compute_score(file, keywords)
            scored_files.append((file_path, score))

        # Sort
        scored_files.sort(key=lambda x: x[1], reverse=True)

        # Step 1: pick top-k
        top_files = [file for file, _ in scored_files[:k]]

        # Step 2: include dependencies
        expanded = set(top_files)

        for file in top_files:
            deps = self.map.get("dependencies", {}).get(file, [])
            expanded.update(deps)

        return list(expanded)

    # -----------------------------
    # SCORING COMPONENTS
    # -----------------------------

    def _compute_score(self, file: Dict, keywords: List[str]) -> float:
        """
        Final scoring formula:

        score = keyword_match + dependency_score - size_penalty
        """

        file_path = file["path"]

        keyword_score = self._keyword_match(file_path, keywords)
        dependency_score = self._dependency_score(file_path)
        size_penalty = self._size_penalty(file["size"])

        return keyword_score + dependency_score - size_penalty

    def _keyword_match(self, file_path: str, keywords: List[str]) -> int:
        """
        Counts how many keywords match file path

        Example:
        query = "add"
        file = math_ops.py → match → +1
        """

        file_path = file_path.lower()

        return sum(1 for kw in keywords if kw in file_path)

    def _dependency_score(self, file_path: str) -> int:
        """
        Boost score if file has dependencies

        WHY?
        → Files with dependencies are more important
        """

        deps = self.map.get("dependencies", {}).get(file_path, [])

        return len(deps)

    def _size_penalty(self, size: int) -> float:
        """
        Penalize large files

        WHY?
        → Large files = more tokens = expensive
        """

        return size / 1000  # normalize

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Simple keyword extraction

        Example:
        "optimize add function" → ["optimize", "add", "function"]
        """

        return query.lower().split()
    
    def _reverse_dependencies(self, file_path):
        reverse = []

        for f, deps in self.map.get("dependencies", {}).items():
            if file_path in deps:
                reverse.append(f)

        return reverse
from typing import List, Dict, Any


class QueryEngine:
    def __init__(self, codebase_map: Dict[str, Any]):
        """
        QueryEngine selects most relevant files for a given user query.

        Input:
        - codebase_map → output of CodebaseMap

        WHY?
        → LLM should not see entire repo
        → Only most relevant files should be selected
        """

        self.map = codebase_map

    def query(self, user_query: str, top_k: int = 5) -> List[str]:
        """
        Main function.

        Steps:
        1. Extract keywords from query
        2. Score each file
        3. Sort by score
        4. Return top_k files

        Example:
        query = "helper function"
        → ["utils.py"]
        """

        keywords = self._extract_keywords(user_query)

        scores = []

        for file in self.map["files"]:
            file_path = file["path"]

            score = self._compute_score(file, keywords)

            scores.append((file_path, score))

        # Sort descending
        scores.sort(key=lambda x: x[1], reverse=True)

        return [file for file, _ in scores[:top_k]]

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Convert query → keywords

        Example:
        "optimize sorting function"
        → ["optimize", "sorting", "function"]
        """
        return query.lower().split()

    def _compute_score(self, file: Dict, keywords: List[str]) -> float:
        """
        Scoring formula:

        score = keyword_match + dependency_score - size_penalty

        WHY:
        → balance relevance + importance + cost
        """

        file_path = file["path"]

        keyword_score = self._keyword_match(file_path, keywords)
        dependency_score = self._dependency_score(file_path)
        size_penalty = file["size"] / 1000

        return keyword_score + dependency_score - size_penalty

    def _keyword_match(self, file_path: str, keywords: List[str]) -> int:
        """
        Match keywords with file name
        """
        return sum(1 for kw in keywords if kw in file_path.lower())

    def _dependency_score(self, file_path: str) -> int:
        """
        More dependencies → more important file
        """
        deps = self.map["dependencies"].get(file_path, [])
        return len(deps)
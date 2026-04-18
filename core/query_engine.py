from typing import List, Dict, Any


class QueryEngine:
    def __init__(self, codebase_map: Dict[str, Any]):
        """
        Initialize QueryEngine with the precomputed codebase map.

        codebase_map contains:
        - files: metadata (path, size)
        - dependencies: file → dependent files

        Why store this?
        → Avoid recomputation
        → Make querying fast and deterministic
        """
        self.map = codebase_map

    def query(self, user_query: str, top_k: int = 5) -> List[str]:
        """
        Main entry point of the Query Engine.

        Steps:
        1. Extract keywords from user query
        2. Score each file based on relevance
        3. Sort files by score
        4. Return top_k most relevant files

        Why?
        → We want to send only the most relevant files to LLM
        → Reduces cost, improves accuracy

        Example:
        Input: "optimize sorting logic"
        Output: ["sort.py", "utils.py"]
        """

        # Step 1: Convert user query into searchable keywords
        keywords = self._extract_keywords(user_query)

        # List to store (file_path, score)
        scores = []

        # Step 2: Compute score for each file
        for file in self.map["files"]:
            file_path = file["path"]

            # Core scoring logic
            score = self._compute_score(file, keywords)

            scores.append((file_path, score))

        # Step 3: Sort files by score (highest first)
        scores.sort(key=lambda x: x[1], reverse=True)

        # Step 4: Return only top_k file paths
        return [file for file, _ in scores[:top_k]]

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from user query.

        Current approach:
        → Lowercase + split by space

        Why simple?
        → Fast
        → Deterministic
        → No LLM dependency

        Future improvement:
        → NLP / embeddings / LLM keyword extraction
        """
        return query.lower().split()

    def _compute_score(self, file: Dict, keywords: List[str]) -> float:
        """
        Core scoring formula:

        score = keyword_match + dependency_score - size_penalty

        Each component:
        1. keyword_match → semantic relevance
        2. dependency_score → structural importance
        3. size_penalty → efficiency constraint

        Why this formula?
        → Balance relevance + importance + cost
        """

        file_path = file["path"]

        # 1. How well file name matches query keywords
        keyword_score = self._keyword_match(file_path, keywords)

        # 2. Boost score if file is structurally important
        # (i.e., connected to other files)
        dependency_score = self._dependency_score(file_path)

        # 3. Penalize large files (LLM context is expensive)
        size_penalty = file["size"] / 1000

        # Final combined score
        return keyword_score + dependency_score - size_penalty

    def _keyword_match(self, file_path: str, keywords: List[str]) -> int:
        """
        Counts how many query keywords appear in file path.

        Example:
        file_path = "utils/sort.py"
        keywords = ["sort"]

        → score = 1

        Why file path?
        → Fast heuristic
        → Often meaningful naming in real projects

        Limitation:
        → Doesn't look inside file content (yet)
        """

        return sum(1 for kw in keywords if kw in file_path.lower())

    def _dependency_score(self, file_path: str) -> int:
        """
        Computes structural importance of file.

        Logic:
        → More dependencies = more important file

        Example:
        main.py → imports utils.py, db.py
        → Higher score

        Why?
        → Central files are more likely relevant
        → Helps expand context intelligently

        Edge case:
        → If file not in dependencies → return 0
        """

        deps = self.map["dependencies"].get(file_path, [])

        # Number of dependencies = importance score
        return len(deps)
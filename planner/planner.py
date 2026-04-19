from typing import List, Dict, Any


class Planner:
    def __init__(self, codebase_map: Dict[str, Any]):
        """
        Planner (Day 13 - STABLE VERSION)

        Responsibilities:
        → Select ONE primary file
        → Create ONE safe step

        WHY?
        → Multi-step + multi-file is unstable right now
        → We stabilize system first, then scale later
        """

        self.map = codebase_map

    def create_plan(self, query: str, selected_files: List[str]) -> List[Dict]:
        """
        Returns a SAFE plan.

        Output:
        [
            {"type": "refactor", "target": "file.py"}
        ]
        """

        if not selected_files:
            return []

        # -----------------------------
        # STEP 1: Identify PRIMARY file
        # -----------------------------
        primary = self._get_primary_file(query, selected_files)

        # -----------------------------
        # STEP 2: Infer step type
        # -----------------------------
        step_type = self._infer_step_type(query)

        # -----------------------------
        # STEP 3: Return SINGLE STEP
        # -----------------------------
        return [{"type": step_type, "target": primary}]

    # =========================================================
    # HELPERS
    # =========================================================

    def _infer_step_type(self, query: str) -> str:
        """
        Decide step type based on query.
        """

        query = query.lower()

        if "rename" in query:
            return "modify_function"

        if "optimize" in query:
            return "refactor"

        return "refactor"

    def _get_primary_file(self, query: str, selected_files: List[str]) -> str:
        """
        Choose MOST relevant file.

        Strategy:
        → Function match (HIGH priority)
        → File name match (LOW priority)
        """

        keywords = query.lower().split()

        best_file = selected_files[0]
        best_score = -1

        for file in selected_files:
            score = 0

            # -----------------------------
            # 1. FILE NAME MATCH
            # -----------------------------
            for kw in keywords:
                if kw in file.lower():
                    score += 2

            # -----------------------------
            # 2. FUNCTION MATCH (STRONG SIGNAL)
            # -----------------------------
            functions = self.map.get("ast", {}).get(file, {}).get("functions", [])

            for func in functions:
                for kw in keywords:
                    if kw in func["name"].lower():
                        score += 5  # 🔥 VERY IMPORTANT

            # -----------------------------
            # Track best
            # -----------------------------
            if score > best_score:
                best_score = score
                best_file = file

        return best_file

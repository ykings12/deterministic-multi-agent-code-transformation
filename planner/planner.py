from typing import List, Dict, Any


class Planner:
    def __init__(self, codebase_map: Dict[str, Any]):
        """
        Planner (Day 21 - Multi-file consistency)

        Responsibilities:
        → Identify primary file
        → Expand dependencies
        → Generate ordered multi-file steps
        """

        self.map = codebase_map

    def create_plan(self, query: str, selected_files: List[str]) -> List[Dict]:
        if not selected_files:
            return []

        # -----------------------------
        # STEP 1: PRIMARY FILE
        # -----------------------------
        primary = self._get_primary_file(query, selected_files)

        # -----------------------------
        # STEP 2: STEP TYPE
        # -----------------------------
        step_type = self._infer_step_type(query)

        # -----------------------------
        # STEP 3: DEPENDENCY EXPANSION
        # -----------------------------
        related_files = self._expand_dependencies(primary)

        # Keep only selected files (important constraint)
        related_files = [f for f in related_files if f in selected_files]

        # Ensure primary is first
        if primary not in related_files:
            related_files.insert(0, primary)

        # -----------------------------
        # STEP 4: BUILD MULTI-STEP PLAN
        # -----------------------------
        steps = []

        # 🔥 Step 1 → modify primary
        steps.append({"type": step_type, "target": primary})

        # 🔥 Step 2+ → update usage in dependents
        for file in related_files:
            if file == primary:
                continue

            steps.append({"type": "update_usage", "target": file})

        return steps

    # =========================================================
    # HELPERS
    # =========================================================

    def _infer_step_type(self, query: str) -> str:
        query = query.lower()

        if "rename" in query:
            return "modify_function"

        return "refactor"

    def _get_primary_file(self, query: str, selected_files: List[str]) -> str:
        keywords = query.lower().split()

        best_file = selected_files[0]
        best_score = -1

        for file in selected_files:
            score = 0

            # File name match
            for kw in keywords:
                if kw in file.lower():
                    score += 2

            # Function match
            functions = self.map.get("ast", {}).get(file, {}).get("functions", [])

            for func in functions:
                for kw in keywords:
                    if kw in func["name"].lower():
                        score += 5

            if score > best_score:
                best_score = score
                best_file = file

        return best_file

    def _expand_dependencies(self, file: str) -> List[str]:
        """
        Get forward + reverse dependencies
        """

        deps = self.map.get("dependencies", {}).get(file, [])

        reverse = [f for f, d in self.map.get("dependencies", {}).items() if file in d]

        return list(set([file] + deps + reverse))

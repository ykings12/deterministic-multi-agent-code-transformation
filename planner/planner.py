from typing import List, Dict


class Planner:
    def __init__(self):
        """
        Planner decides HOW MANY steps are needed.

        WHY?
        → Multi-file changes cannot be done in one shot
        → Break into smaller steps
        """

    def create_plan(self, query: str, selected_files: List[str]) -> List[Dict]:
        """
        Returns a list of steps.

        Example:
        [
            {"type": "modify_function", "target": "math_ops.py"},
            {"type": "update_usage", "target": "main.py"}
        ]
        """

        steps = []

        # 🔥 Simple heuristic planning
        query_lower = query.lower()

        # Case 1: rename / modify function
        if "rename" in query_lower:
            for file in selected_files:
                steps.append({"type": "modify_function", "target": file})

        # Case 2: general refactor
        else:
            for file in selected_files:
                steps.append({"type": "refactor", "target": file})

        return steps

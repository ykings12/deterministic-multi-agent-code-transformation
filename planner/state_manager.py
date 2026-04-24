from typing import Dict, Any, List


class StateManager:
    """
    Central memory system for pipeline.

    WHY?
    → Maintain global state across steps
    → Track history
    → Enable intelligent retries
    """

    def __init__(self):
        self.state: Dict[str, Any] = {}

    def initialize(
        self,
        query: str,
        selected_files: List[str],
        context: List[Dict],
        steps: List[Dict],
    ):
        """
        Initialize state at start of pipeline.
        """

        self.state = {
            "query": query,
            "selected_files": selected_files,
            "context": context,
            "steps": steps,
            "current_step_index": 0,
            "history": [],
            "errors": [],
        }

    def get_current_step(self) -> Dict:
        return self.state["steps"][self.state["current_step_index"]]

    def next_step(self):
        self.state["current_step_index"] += 1

    def add_history(self, step: Dict, output: str, review: Dict):
        """
        Store execution history.
        """

        self.state["history"].append({"step": step, "output": output, "review": review})

    def add_error(self, issue: str):
        self.state["errors"].append(issue)

    def has_more_steps(self) -> bool:
        return self.state["current_step_index"] < len(self.state["steps"])

    def get_state(self) -> Dict:
        return self.state

from typing import Dict, List
from executor.executor import Executor


class StepExecutor:
    def __init__(self, executor: Executor):
        """
        Executes ONE step at a time.

        WHY?
        → Prevent multi-file confusion
        → Enable step-level retry with feedback
        """

        self.executor = executor

    def execute_step(self, context: List[Dict], step: Dict, task: str) -> str:
        """
        Execute a single step.

        FIX:
        → Accept external task (which includes feedback)
        → Do NOT override task internally
        """

        result = self.executor.run(context, task)

        return result[0]["suggestion"]

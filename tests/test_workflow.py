import unittest

from graph.workflow import WorkflowState


class TestWorkflowState(unittest.TestCase):

    def test_initialization(self):
        state = WorkflowState("test query")

        self.assertEqual(state.query, "test query")
        self.assertEqual(state.selected_files, [])
        self.assertEqual(state.context, [])
        self.assertEqual(state.steps, [])
        self.assertFalse(state.success)


class MockExecutor:
    def execute_step(self, context, step, task):
        return "FILE: test.py\ndef foo():\n    pass"


class MockReviewer:
    def review(self, context, output):
        return {"valid": True, "score": 1, "issues": []}


class MockEditor:
    def apply_changes(self, output):
        self.applied = True


class TestWorkflowExecution(unittest.TestCase):

    def test_basic_flow(self):
        from graph.workflow import Workflow

        workflow = Workflow(
            budget=None,
            selector=None,
            builder=None,
            planner=None,
            step_executor=MockExecutor(),
            reviewer=MockReviewer(),
            editor=MockEditor(),
        )

        state = WorkflowState("test")
        state.context = [{"file": "test.py"}]
        state.current_step = {"type": "refactor", "target": "test.py"}

        state = workflow.execute_step(state)
        state = workflow.review(state)

        self.assertTrue(state.success)


if __name__ == "__main__":
    unittest.main()

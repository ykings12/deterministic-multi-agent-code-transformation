from executor.step_executor import StepExecutor


class MockExecutor:
    def run(self, context, task):
        return [{"suggestion": "FILE: test.py\ndef foo(): pass"}]


def test_step_execution():
    executor = StepExecutor(MockExecutor())

    output = executor.execute_step([], {"type": "refactor", "target": "test.py"})

    assert "FILE:" in output

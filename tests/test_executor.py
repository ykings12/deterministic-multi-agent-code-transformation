from executor.executor import Executor


def test_executor_basic():
    executor = Executor()

    context = [
        {"file": "a.py", "code": "print(1)"}
    ]

    result = executor.run(context, "optimize code")

    assert result[0]["file"] == "a.py"
    assert "optimize code" in result[0]["suggestion"]
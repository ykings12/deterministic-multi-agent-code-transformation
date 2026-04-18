from executor.executor import Executor


def test_executor_mock():
    executor = Executor(use_llm=False)

    context = [{"file": "a.py", "code": "print(1)"}]

    result = executor.run(context, "optimize code")

    assert "Mocked" in result[0]["suggestion"]


def test_invalid_provider():
    executor = Executor(use_llm=True, provider="invalid")

    try:
        executor._call_llm("test")
    except ValueError as e:
        assert "Unsupported" in str(e)
from reviewer.reviewer import Reviewer


def test_valid_output():
    reviewer = Reviewer()

    original = [{"file": "a.py", "code": "def f(): return 1"}]

    output = """FILE: a.py
def f():
    return 1
"""

    result = reviewer.review(original, output)

    assert result["valid"] is True


def test_invalid_format():
    reviewer = Reviewer()

    original = [{"file": "a.py", "code": "x=1"}]

    output = "invalid output"

    result = reviewer.review(original, output)

    assert result["valid"] is False


def test_syntax_error():
    reviewer = Reviewer()

    original = [{"file": "a.py", "code": "x=1"}]

    output = """FILE: a.py
def broken(
"""

    result = reviewer.review(original, output)

    assert result["valid"] is False
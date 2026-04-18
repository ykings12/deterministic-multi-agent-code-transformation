import pytest
from planner.context_budget import ContextBudget


@pytest.fixture
def sample_map():
    return {
        "files": [
            {"path": "main.py", "size": 100},
            {"path": "utils.py", "size": 200},
            {"path": "math_ops.py", "size": 50},
        ],
        "dependencies": {
            "main.py": ["utils.py"],
            "utils.py": [],
            "math_ops.py": []
        }
    }


def test_keyword_match(sample_map):
    cb = ContextBudget(sample_map)

    score = cb._keyword_match("math_ops.py", ["add"])
    assert score == 0

    score = cb._keyword_match("math_ops.py", ["math"])
    assert score == 1


def test_dependency_score(sample_map):
    cb = ContextBudget(sample_map)

    assert cb._dependency_score("main.py") == 1
    assert cb._dependency_score("utils.py") == 0


def test_size_penalty(sample_map):
    cb = ContextBudget(sample_map)

    assert cb._size_penalty(1000) == 1.0
    assert cb._size_penalty(500) == 0.5


def test_compute_score(sample_map):
    cb = ContextBudget(sample_map)

    file = {"path": "main.py", "size": 100}
    score = cb._compute_score(file, ["main"])

    assert score > 0


def test_select_top_k(sample_map):
    cb = ContextBudget(sample_map)

    result = cb.select_top_k("math", k=1)

    assert result[0] == "math_ops.py"


def test_select_top_k_limit(sample_map):
    cb = ContextBudget(sample_map)

    result = cb.select_top_k("py", k=2)

    assert len(result) == 2
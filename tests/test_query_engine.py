from planner.query_engine import QueryEngine


def test_function_match():
    mock_map = {
        "files": [{"path": "utils.py", "size": 100}],
        "ast": {
            "utils.py": {
                "functions": [{"name": "helper"}]
            }
        },
        "dependencies": {},
        "call_graph": {}
    }

    engine = QueryEngine(mock_map)

    result = engine.query("helper")

    assert result[0] == "utils.py"


def test_call_graph_match():
    mock_map = {
        "files": [{"path": "main.py", "size": 100}],
        "ast": {"main.py": {"functions": []}},
        "dependencies": {},
        "call_graph": {
            "main.py::run": ["helper"]
        }
    }

    engine = QueryEngine(mock_map)

    result = engine.query("helper")

    assert result[0] == "main.py"
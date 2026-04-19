from planner.function_selector import FunctionSelector


def test_function_selection():
    codebase_map = {
        "ast": {
            "utils.py": {
                "functions": [
                    {"name": "helper"},
                    {"name": "format"}
                ]
            }
        }
    }

    selector = FunctionSelector(codebase_map)

    result = selector.select_functions(["utils.py"], "helper")

    assert len(result) == 1
    assert result[0]["function"] == "helper"
from planner.planner import Planner


def test_primary_selection():
    code_map = {"dependencies": {}}
    planner = Planner(code_map)

    files = ["utils.py", "data_processor.py"]

    primary = planner._get_primary_file("process data", files)

    assert primary == "data_processor.py"


def test_dependency_expansion():
    code_map = {"dependencies": {"a.py": ["b.py"], "b.py": []}}

    planner = Planner(code_map)

    result = planner._expand_dependencies("a.py")

    assert "b.py" in result

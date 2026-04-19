from planner.planner import Planner


def test_simple_plan():
    planner = Planner()

    plan = planner.create_plan("refactor code", ["a.py"])

    assert len(plan) == 1
    assert plan[0]["type"] == "refactor"


def test_rename_plan():
    planner = Planner()

    plan = planner.create_plan("rename function", ["a.py", "b.py"])

    assert len(plan) == 2

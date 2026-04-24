from planner.state_manager import StateManager


def test_state_initialization():
    sm = StateManager()

    sm.initialize(
        query="test",
        selected_files=["a.py"],
        context=[{"file": "a.py"}],
        steps=[{"type": "refactor", "target": "a.py"}],
    )

    state = sm.get_state()

    assert state["query"] == "test"
    assert len(state["steps"]) == 1


def test_step_progression():
    sm = StateManager()

    sm.initialize("q", ["a.py"], [], [{"type": "refactor", "target": "a.py"}])

    assert sm.has_more_steps()

    step = sm.get_current_step()
    assert step["target"] == "a.py"

    sm.next_step()
    assert not sm.has_more_steps()

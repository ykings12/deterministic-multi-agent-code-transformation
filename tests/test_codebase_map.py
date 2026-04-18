import os
import tempfile
from core.codebase_map import CodebaseMap


def create_file(path, content=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_codebase_map_basic():
    with tempfile.TemporaryDirectory() as tmp:
        # Create files
        create_file(os.path.join(tmp, "b.py"))
        create_file(os.path.join(tmp, "a.py"), """
import b

def foo():
    bar()

def bar():
    pass
""")

        cb_map = CodebaseMap(tmp)
        result = cb_map.build()

        # Files exist
        assert len(result["files"]) == 2

        # AST exists
        assert "a.py" in result["ast"]
        assert len(result["ast"]["a.py"]["functions"]) == 2

        # Dependency exists
        assert "b.py" in result["dependencies"]["a.py"]

        # Call graph exists
        assert "a.py::foo" in result["call_graph"]
        assert "bar" in result["call_graph"]["a.py::foo"]


def test_empty_repo():
    with tempfile.TemporaryDirectory() as tmp:
        cb_map = CodebaseMap(tmp)
        result = cb_map.build()

        assert result["files"] == []
        assert result["ast"] == {}
        assert result["dependencies"] == {}
        assert result["call_graph"] == {}
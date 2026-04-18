import os
import tempfile
from core.dependency_graph import DependencyGraph


def create_file(path, content=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_simple_import():
    with tempfile.TemporaryDirectory() as tmp:
        # Create files
        create_file(os.path.join(tmp, "b.py"))
        create_file(os.path.join(tmp, "a.py"), "import b")

        graph = DependencyGraph(tmp)

        result = graph.build([os.path.join(tmp, "a.py")])

        assert "a.py" in result
        assert "b.py" in result["a.py"]


def test_from_import():
    with tempfile.TemporaryDirectory() as tmp:
        create_file(os.path.join(tmp, "utils.py"))
        create_file(os.path.join(tmp, "main.py"), "from utils import x")

        graph = DependencyGraph(tmp)

        result = graph.build([os.path.join(tmp, "main.py")])

        assert "utils.py" in result["main.py"]


def test_nested_import():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "pkg"))

        create_file(os.path.join(tmp, "pkg", "mod.py"))
        create_file(os.path.join(tmp, "a.py"), "import pkg.mod")

        graph = DependencyGraph(tmp)

        result = graph.build([os.path.join(tmp, "a.py")])

        assert "pkg/mod.py" in result["a.py"]


def test_ignore_external_import():
    with tempfile.TemporaryDirectory() as tmp:
        create_file(os.path.join(tmp, "a.py"), "import os")

        graph = DependencyGraph(tmp)

        result = graph.build([os.path.join(tmp, "a.py")])

        # os is not inside repo → ignored
        assert result["a.py"] == []


def test_invalid_python_file():
    with tempfile.TemporaryDirectory() as tmp:
        create_file(os.path.join(tmp, "bad.py"), "import ")

        graph = DependencyGraph(tmp)

        result = graph.build([os.path.join(tmp, "bad.py")])

        assert result["bad.py"] == []


def test_multiple_imports():
    with tempfile.TemporaryDirectory() as tmp:
        create_file(os.path.join(tmp, "b.py"))
        create_file(os.path.join(tmp, "c.py"))

        create_file(os.path.join(tmp, "a.py"), """
import b
import c
""")

        graph = DependencyGraph(tmp)

        result = graph.build([os.path.join(tmp, "a.py")])

        assert len(result["a.py"]) == 2


def test_empty_file():
    with tempfile.TemporaryDirectory() as tmp:
        create_file(os.path.join(tmp, "a.py"), "")

        graph = DependencyGraph(tmp)

        result = graph.build([os.path.join(tmp, "a.py")])

        assert result["a.py"] == []
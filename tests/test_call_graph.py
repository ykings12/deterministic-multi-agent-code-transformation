import os
import tempfile
from core.call_graph import CallGraph


def create_file(path, content=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_simple_function_call():
    code = """
def foo():
    bar()

def bar():
    pass
"""
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "a.py")
        create_file(file_path, code)

        graph = CallGraph(tmp)
        result = graph.build([file_path])

        assert "a.py::foo" in result
        assert "bar" in result["a.py::foo"]


def test_multiple_calls():
    code = """
def foo():
    a()
    b()

def a(): pass
def b(): pass
"""
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "a.py")
        create_file(file_path, code)

        graph = CallGraph(tmp)
        result = graph.build([file_path])

        assert len(result["a.py::foo"]) == 2


def test_method_call():
    code = """
def foo():
    obj.method()
"""
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "a.py")
        create_file(file_path, code)

        graph = CallGraph(tmp)
        result = graph.build([file_path])

        assert "method" in result["a.py::foo"]


def test_nested_calls():
    code = """
def foo():
    bar(baz())

def bar(x): pass
def baz(): pass
"""
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "a.py")
        create_file(file_path, code)

        graph = CallGraph(tmp)
        result = graph.build([file_path])

        assert "bar" in result["a.py::foo"]
        assert "baz" in result["a.py::foo"]


def test_invalid_file():
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "bad.py")
        create_file(file_path, "def broken(")

        graph = CallGraph(tmp)
        result = graph.build([file_path])

        assert result == {}


def test_empty_file():
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "empty.py")
        create_file(file_path, "")

        graph = CallGraph(tmp)
        result = graph.build([file_path])

        assert result == {}
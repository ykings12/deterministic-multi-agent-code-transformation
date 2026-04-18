import os
import tempfile
from core.ast_parser import ASTParser


def create_file(path, content=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_function_extraction():
    code = """
def add(a, b):
    return a + b
"""
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "a.py")
        create_file(file_path, code)

        parser = ASTParser()
        result = parser.parse_file(file_path)

        assert len(result["functions"]) == 1
        assert result["functions"][0]["name"] == "add"
        assert result["functions"][0]["args"] == ["a", "b"]


def test_class_extraction():
    code = """
class A:
    def foo(self):
        pass
"""
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "a.py")
        create_file(file_path, code)

        parser = ASTParser()
        result = parser.parse_file(file_path)

        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "A"
        assert len(result["classes"][0]["methods"]) == 1


def test_docstring():
    code = '''
def foo():
    """hello"""
    pass
'''
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "a.py")
        create_file(file_path, code)

        parser = ASTParser()
        result = parser.parse_file(file_path)

        assert result["functions"][0]["docstring"] == "hello"


def test_invalid_file():
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "bad.py")
        create_file(file_path, "def broken(")

        parser = ASTParser()
        result = parser.parse_file(file_path)

        assert result["functions"] == []
        assert result["classes"] == []


def test_empty_file():
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "empty.py")
        create_file(file_path, "")

        parser = ASTParser()
        result = parser.parse_file(file_path)

        assert result["functions"] == []
        assert result["classes"] == []
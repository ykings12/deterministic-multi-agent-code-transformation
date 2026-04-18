import os
import tempfile
from planner.context_builder import ContextBuilder


def create_file(path, content=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def get_mock_map():
    return {
        "ast": {
            "a.py": {
                "functions": [{"name": "foo"}],
                "classes": []
            }
        }
    }


def test_basic_context_build():
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "a.py")
        create_file(file_path, "def foo(): pass")

        builder = ContextBuilder(get_mock_map(), tmp)

        result = builder.build_context(["a.py"])

        assert len(result) == 1
        assert result[0]["file"] == "a.py"
        assert "def foo()" in result[0]["code"]


def test_ast_integration():
    with tempfile.TemporaryDirectory() as tmp:
        create_file(os.path.join(tmp, "a.py"), "def foo(): pass")

        builder = ContextBuilder(get_mock_map(), tmp)
        result = builder.build_context(["a.py"])

        assert result[0]["functions"][0]["name"] == "foo"


def test_missing_file():
    with tempfile.TemporaryDirectory() as tmp:
        builder = ContextBuilder(get_mock_map(), tmp)

        result = builder.build_context(["missing.py"])

        assert result[0]["code"] == ""


def test_multiple_files():
    with tempfile.TemporaryDirectory() as tmp:
        create_file(os.path.join(tmp, "a.py"), "x=1")
        create_file(os.path.join(tmp, "b.py"), "y=2")

        builder = ContextBuilder({"ast": {}}, tmp)

        result = builder.build_context(["a.py", "b.py"])

        assert len(result) == 2
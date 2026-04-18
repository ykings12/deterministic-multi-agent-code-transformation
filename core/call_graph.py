import ast
import os
from typing import Dict, List


class CallGraph:
    def __init__(self, repo_path: str):
        """
        Builds function-level call relationships.

        Example:
        foo() calls bar()

        Output:
        "a.py::foo" → ["bar"]

        WHY?
        → Understand execution flow
        → Enables safe refactoring later
        """

        self.repo_path = os.path.abspath(repo_path)

        # Final structure:
        # {
        #   "a.py::foo": ["bar", "baz"]
        # }
        self.call_graph: Dict[str, List[str]] = {}

    def build(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Build call graph for all files.

        Steps:
        1. Extract functions
        2. For each function → find calls

        WHY:
        → Function-level intelligence
        """

        for file_path in file_paths:
            relative_path = os.path.relpath(file_path, self.repo_path).replace("\\", "/")

            # Extract all functions in file
            functions = self._extract_functions(file_path)

            for func_name, func_node in functions.items():
                # Unique function identifier
                # Example: a.py::foo
                full_func_name = f"{relative_path}::{func_name}"

                # Find all calls inside this function
                called_functions = self._extract_calls(func_node)

                self.call_graph[full_func_name] = called_functions

        return self.call_graph

    def _extract_functions(self, file_path: str) -> Dict[str, ast.FunctionDef]:
        """
        Extract all functions from file.

        Output:
        {
          "foo": <AST node>,
          "bar": <AST node>
        }

        WHY return nodes?
        → Needed to inspect function body later
        """

        functions = {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions[node.name] = node

        except Exception:
            return {}

        return functions

    def _extract_calls(self, func_node: ast.FunctionDef) -> List[str]:
        """
        Extract function calls inside a function.

        Example:
        def foo():
            bar()
            baz()

        Output:
        ["bar", "baz"]
        """

        calls = []

        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)

                if func_name:
                    calls.append(func_name)

        return calls

    def _get_call_name(self, node: ast.Call) -> str:
        """
        Extract function name from call node.

        Handles:
        1. foo()
        2. obj.method()

        Examples:
        foo() → "foo"
        obj.method() → "method"

        WHY needed?
        → AST represents calls differently depending on type
        """

        # Case 1: Direct function call
        if isinstance(node.func, ast.Name):
            return node.func.id

        # Case 2: Method call (object.method())
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr

        # Unknown case
        return ""
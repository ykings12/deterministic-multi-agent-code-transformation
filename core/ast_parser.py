import ast
from typing import Dict, List, Any


class ASTParser:
    def __init__(self):
        """
        AST Parser extracts structural information from Python files.

        WHY?
        → Raw text is unreliable
        → AST gives structured representation

        Output:
        {
            "functions": [...],
            "classes": [...]
        }
        """
        pass

    def parse_file(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Main entry point.

        Steps:
        1. Read file
        2. Convert to AST
        3. Extract functions and classes

        WHY?
        → Centralized parsing logic
        → Used by CodebaseMap
        """

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            # Convert code → AST
            tree = ast.parse(source_code)

            return {
                "functions": self._extract_functions(tree),
                "classes": self._extract_classes(tree),
            }

        except Exception:
            # If file is invalid Python → safe fallback
            return {"functions": [], "classes": []}

    def _extract_functions(self, tree: ast.AST) -> List[Dict]:
        """
        Extract all function definitions.

        Example:
        def add(a, b):
            return a + b

        Output:
        {
            "name": "add",
            "start_line": 1,
            "end_line": 2,
            "docstring": None,
            "args": ["a", "b"]
        }
        """

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,

                    # Line numbers (important for edit layer later)
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),

                    # Extract docstring if exists
                    "docstring": ast.get_docstring(node),

                    # Extract argument names
                    "args": [arg.arg for arg in node.args.args],
                })

        return functions

    def _extract_classes(self, tree: ast.AST) -> List[Dict]:
        """
        Extract class definitions.

        Example:
        class A:
            def foo(self): pass

        Output:
        {
            "name": "A",
            "methods": [...]
        }
        """

        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "docstring": ast.get_docstring(node),

                    # Extract methods inside class
                    "methods": self._extract_class_methods(node),
                })

        return classes

    def _extract_class_methods(self, class_node: ast.ClassDef) -> List[Dict]:
        """
        Extract methods inside a class.

        WHY separate?
        → Class body is different from global scope
        """

        methods = []

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                methods.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "args": [arg.arg for arg in node.args.args],
                })

        return methods
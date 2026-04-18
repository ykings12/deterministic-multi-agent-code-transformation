import ast
import os
from typing import Dict, List


class DependencyGraph:
    def __init__(self, repo_path: str):
        # Store absolute repo path for normalization
        self.repo_path = os.path.abspath(repo_path)

        # Final output: file → list of dependent files
        self.dependencies: Dict[str, List[str]] = {}

    def build(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Main entry point:
        Takes list of Python file paths and builds dependency graph
        """
        for file_path in file_paths:
            relative_path = os.path.relpath(file_path, self.repo_path).replace("\\", "/")

            imports = self._extract_imports(file_path)

            # Normalize imports → actual file paths
            resolved_imports = self._resolve_imports(imports)

            self.dependencies[relative_path] = resolved_imports

        return self.dependencies

    def _extract_imports(self, file_path: str) -> List[str]:
        """
        Extract raw import statements using AST
        Handles:
        - import module
        - from module import something
        """
        imports = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                # Case: import x
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)

                # Case: from x import y
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

        except Exception:
            # If parsing fails, return empty imports
            return []

        return imports

    def _resolve_imports(self, imports: List[str]) -> List[str]:
        """
        Convert module names → actual file paths inside repo
        Example:
        utils.helper → utils/helper.py
        """
        resolved = []

        for module in imports:
            # Convert module to file path
            module_path = module.replace(".", "/") + ".py"

            full_path = os.path.join(self.repo_path, module_path)

            # Only include if file exists in repo
            if os.path.exists(full_path):
                relative_path = os.path.relpath(full_path, self.repo_path).replace("\\", "/")
                resolved.append(relative_path)

        return resolved
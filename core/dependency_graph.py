import ast
import os
from typing import Dict, List


class DependencyGraph:
    def __init__(self, repo_path: str):
        """
        Initialize Dependency Graph builder.

        repo_path:
        → Root directory of the repository

        Why store absolute path?
        → Ensures consistent path resolution across OS
        → Avoids relative path confusion
        """
        self.repo_path = os.path.abspath(repo_path)

        # Final structure:
        # {
        #   "a.py": ["b.py", "utils/helper.py"]
        # }
        self.dependencies: Dict[str, List[str]] = {}

    def build(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Build dependency graph for given files.

        Input:
        → List of absolute file paths

        Output:
        → Mapping: file → imported files

        Example:
        a.py contains: import b
        Output:
        { "a.py": ["b.py"] }

        WHY:
        → Helps understand file relationships
        → Used later for context expansion
        """

        for file_path in file_paths:
            # Convert absolute path → relative path
            relative_path = os.path.relpath(file_path, self.repo_path).replace("\\", "/")

            # Step 1: Extract raw import statements
            imports = self._extract_imports(file_path)

            # Step 2: Convert imports → actual file paths
            resolved_imports = self._resolve_imports(imports)

            # Store result
            self.dependencies[relative_path] = resolved_imports

        return self.dependencies

    def _extract_imports(self, file_path: str) -> List[str]:
        """
        Extract import statements using AST.

        Handles:
        1. import module
        2. from module import something

        Example:
        import utils.helper
        → "utils.helper"

        from utils import helper
        → "utils"

        WHY AST?
        → Avoids string parsing errors
        → Reliable structure

        Returns:
        → List of module names (NOT file paths yet)
        """

        imports = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            # Traverse AST
            for node in ast.walk(tree):

                # Case 1: import x
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Example: import utils.helper
                        imports.append(alias.name)

                # Case 2: from x import y
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Example: from utils import helper
                        imports.append(node.module)

        except Exception:
            # If file is invalid Python → return empty
            return []

        return imports

    def _resolve_imports(self, imports: List[str]) -> List[str]:
        """
        Convert module names → actual file paths inside repo.

        Example:
        "utils.helper" → "utils/helper.py"

        WHY?
        → AST gives module names, but we need file paths

        Steps:
        1. Replace "." with "/"
        2. Append ".py"
        3. Check if file exists

        Only include:
        → Files inside repo (ignore external libraries)
        """

        resolved = []

        for module in imports:
            # Convert module to path
            # Example: utils.helper → utils/helper.py
            module_path = module.replace(".", "/") + ".py"

            full_path = os.path.join(self.repo_path, module_path)

            # Only include if file exists inside repo
            if os.path.exists(full_path):
                relative_path = os.path.relpath(full_path, self.repo_path).replace("\\", "/")
                resolved.append(relative_path)

        return resolved
import os
import json
from typing import Dict, List, Optional


class RepositoryIndexer:
    def __init__(self, repo_path: str):
        """
        Initializes repository indexer.

        repo_path:
        → root directory of project
        """
        self.repo_path = os.path.abspath(repo_path)

        # Final structure:
        # {
        #   "files": [
        #       {"path": "a.py", "size": 123, ...}
        #   ]
        # }
        self.index: Dict[str, List[Dict]] = {"files": []}

    def is_python_file(self, filename: str) -> bool:
        """Check if file is Python file"""
        return filename.endswith(".py")

    def should_ignore(self, path: str) -> bool:
        """Ignore system folders"""
        ignore_dirs = ["__pycache__", ".git", ".venv"]
        return any(ignored in path for ignored in ignore_dirs)

    def get_file_metadata(self, file_path: str) -> Optional[Dict]:
        """
        Extract metadata from file.
        """
        try:
            size = os.path.getsize(file_path)

            # Skip large files
            if size > 1_000_000:
                return None

            last_modified = os.path.getmtime(file_path)

            relative_path = os.path.relpath(file_path, self.repo_path)

            return {
                "path": relative_path.replace("\\", "/"),
                "size": size,
                "last_modified": int(last_modified),
            }

        except Exception:
            return None

    def build_index(self) -> None:
        """
        Traverse repo and collect Python files
        """
        for root, dirs, files in os.walk(self.repo_path):

            if self.should_ignore(root):
                continue

            for file in files:
                if self.is_python_file(file):
                    full_path = os.path.join(root, file)

                    metadata = self.get_file_metadata(full_path)

                    if metadata:
                        self.index["files"].append(metadata)

    def save_index(self, output_path: str = "data/codebase_map.json") -> None:
        """Save JSON output"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(self.index, f, indent=4)
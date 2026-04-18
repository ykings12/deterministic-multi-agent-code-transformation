import os
from typing import Dict, Any

from core.indexer import RepositoryIndexer
from core.ast_parser import ASTParser
from core.dependency_graph import DependencyGraph
from core.call_graph import CallGraph


class CodebaseMap:
    def __init__(self, repo_path: str):
        """
        Central orchestrator for building complete code intelligence.

        This class combines ALL components:
        - Indexer (files)
        - AST Parser (structure)
        - Dependency Graph (file relationships)
        - Call Graph (function relationships)

        WHY?
        → Single unified data structure
        → Easy for planner to consume
        """

        self.repo_path = repo_path

        # Initialize all subsystems
        self.indexer = RepositoryIndexer(repo_path)
        self.ast_parser = ASTParser()
        self.dependency_graph = DependencyGraph(repo_path)
        self.call_graph = CallGraph(repo_path)

        # Final output structure
        self.map: Dict[str, Any] = {}

    def build(self) -> Dict[str, Any]:
        """
        Main pipeline that builds complete codebase understanding.

        Pipeline steps:
        1. Index files
        2. Parse AST
        3. Build dependency graph
        4. Build call graph
        5. Combine everything

        WHY PIPELINE?
        → Each step depends on previous
        → Clean modular design
        """

        # ---------------------------
        # STEP 1: FILE INDEXING
        # ---------------------------
        # Finds all Python files + metadata
        self.indexer.build_index()
        files_metadata = self.indexer.index["files"]

        # Convert relative paths → absolute paths
        file_paths = [
            os.path.join(self.repo_path, f["path"])
            for f in files_metadata
        ]

        # ---------------------------
        # STEP 2: AST PARSING
        # ---------------------------
        # Extract functions + classes per file
        ast_data = {}

        for file_meta in files_metadata:
            relative_path = file_meta["path"]
            full_path = os.path.join(self.repo_path, relative_path)

            # Parse file structure
            ast_data[relative_path] = self.ast_parser.parse_file(full_path)

        # ---------------------------
        # STEP 3: DEPENDENCY GRAPH
        # ---------------------------
        # File → file relationships
        dependencies = self.dependency_graph.build(file_paths)

        # ---------------------------
        # STEP 4: CALL GRAPH
        # ---------------------------
        # Function → function relationships
        call_graph = self.call_graph.build(file_paths)

        # ---------------------------
        # STEP 5: COMBINE EVERYTHING
        # ---------------------------
        self.map = {
            "files": files_metadata,
            "ast": ast_data,
            "dependencies": dependencies,
            "call_graph": call_graph,
        }

        return self.map
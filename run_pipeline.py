import os
import tempfile

from core.codebase_map import CodebaseMap
from planner.query_engine import QueryEngine
from planner.context_builder import ContextBuilder
from executor.executor import Executor


def create_file(path, content=""):
    with open(path, "w") as f:
        f.write(content)


def main():
    print("🚀 Running Pipeline...\n")

    with tempfile.TemporaryDirectory() as tmp:

        # -----------------------------------
        # STEP 1: Create sample repo
        # -----------------------------------
        create_file(os.path.join(tmp, "utils.py"), """
def helper():
    return "hello"
""")

        create_file(os.path.join(tmp, "main.py"), """
import utils

def run():
    helper()
""")

        create_file(os.path.join(tmp, "math_ops.py"), """
def add(a, b):
    return a + b
""")

        # -----------------------------------
        # STEP 2: Build Codebase Map
        # -----------------------------------
        cb = CodebaseMap(tmp)
        code_map = cb.build()

        # -----------------------------------
        # STEP 3: Query Engine
        # -----------------------------------
        engine = QueryEngine(code_map)
        builder = ContextBuilder(code_map, tmp)

        queries = ["helper", "run", "add"]

        # Executor (DEBUG OFF for clean output)
        executor = Executor(use_llm=True, debug=False)

        for query in queries:
            print(f"\n🔍 Query: {query}")

            selected_files = engine.query(query)

            context = builder.build_context(selected_files)

            result = executor.run(context, f"Optimize code for: {query}")

            print("\n🤖 Output:\n")
            print(result[0]["suggestion"])

            print("\n" + "-" * 50)


if __name__ == "__main__":
    main()
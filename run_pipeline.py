import os
import tempfile

from core.codebase_map import CodebaseMap
from planner.query_engine import QueryEngine
from planner.context_builder import ContextBuilder


def create_file(path, content=""):
    with open(path, "w") as f:
        f.write(content)


def main():
    print("🚀 Running End-to-End Pipeline...\n")

    with tempfile.TemporaryDirectory() as tmp:
        print(f"📁 Temp Repo: {tmp}\n")

        # Step 1: Create sample repo
        create_file(os.path.join(tmp, "utils.py"), """
def helper():
    return "hello"
""")

        create_file(os.path.join(tmp, "main.py"), """
import utils

def run():
    helper()
""")

        print("✅ Files created: utils.py, main.py\n")

        # Step 2: Build Codebase Map
        cb = CodebaseMap(tmp)
        code_map = cb.build()

        print("📦 CODEBASE MAP:")
        print(code_map)
        print("\n" + "-"*50 + "\n")

        # Step 3: Query
        engine = QueryEngine(code_map)
        selected_files = engine.query("helper")

        print("🔍 SELECTED FILES:")
        print(selected_files)
        print("\n" + "-"*50 + "\n")

        # Step 4: Context Builder
        builder = ContextBuilder(code_map, tmp)
        context = builder.build_context(selected_files)

        print("📜 FINAL CONTEXT (LLM INPUT):\n")
        for item in context:
            print(f"File: {item['file']}")
            print("Code:")
            print(item["code"])
            print("Functions:", item["functions"])
            print("\n" + "-"*30 + "\n")


if __name__ == "__main__":
    main()
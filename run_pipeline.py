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

        print("✅ Files created: utils.py, main.py, math_ops.py\n")

        # -----------------------------------
        # STEP 2: Build Codebase Map
        # -----------------------------------
        cb = CodebaseMap(tmp)
        code_map = cb.build()

        print("📦 CODEBASE MAP:")
        print(code_map)
        print("\n" + "="*60 + "\n")

        # -----------------------------------
        # STEP 3: Test multiple queries
        # -----------------------------------
        engine = QueryEngine(code_map)

        queries = [
            "helper",     # should match utils.py + main.py
            "run",        # should match main.py
            "add",        # should match math_ops.py
        ]

        for query in queries:
            print(f"🔍 QUERY: '{query}'")

            selected_files = engine.query(query)

            print("➡️ Selected Files:", selected_files)

            # -----------------------------------
            # STEP 4: Context Builder
            # -----------------------------------
            builder = ContextBuilder(code_map, tmp)
            context = builder.build_context(selected_files)

            print("\n📜 CONTEXT:\n")

            for item in context:
                print(f"📄 File: {item['file']}")
                print("Code:")
                print(item["code"])
                print("Functions:", [f["name"] for f in item["functions"]])
                print("-" * 40)

            print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
import os
import tempfile

from core.codebase_map import CodebaseMap
from planner.query_engine import QueryEngine
from planner.context_builder import ContextBuilder
from executor.executor import Executor
from reviewer.reviewer import Reviewer


def create_file(path, content=""):
    with open(path, "w") as f:
        f.write(content)


def build_feedback(issues):
    instructions = "\nREVIEW FEEDBACK:\n"

    for issue in issues:

        if "Invalid format" in issue:
            instructions += "- Use EXACT format: FILE: <filename>\n"

        if "Duplicate file" in issue:
            instructions += "- Each file must appear ONLY ONCE\n"

        if "Logic change" in issue:
            instructions += "- DO NOT change return values\n"
            instructions += "- Preserve behavior exactly\n"

        if "Function call change" in issue:
            instructions += "- DO NOT modify function calls\n"

        if "Unauthorized file" in issue:
            instructions += "- ONLY modify allowed files\n"

    instructions += "\nFix ALL issues in ONE response.\n"
    return instructions


def main():
    print("🚀 Running Pipeline...\n")

    with tempfile.TemporaryDirectory() as tmp:

        # -----------------------------
        # CREATE FILES
        # -----------------------------
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

        # -----------------------------
        # BUILD SYSTEM
        # -----------------------------
        cb = CodebaseMap(tmp)
        code_map = cb.build()

        engine = QueryEngine(code_map)
        builder = ContextBuilder(code_map, tmp)

        executor = Executor(use_llm=True, debug=False)
        reviewer = Reviewer()

        queries = ["helper", "run", "add"]
        MAX_RETRIES = 4

        for query in queries:
            print(f"\n🔍 Query: {query}")

            selected_files = engine.query(query)
            context = builder.build_context(selected_files)

            attempt = 0
            success = False
            feedback = ""

            while attempt < MAX_RETRIES:

                task = f"Refactor code WITHOUT changing behavior: {query}\n{feedback}"

                result = executor.run(context, task)
                output = result[0]["suggestion"]

                review = reviewer.review(context, output)

                print("\n🤖 LLM OUTPUT:\n")
                print(output)

                print("\n🔍 REVIEW RESULT:")
                print(review)

                if review["valid"]:
                    print("\n✅ ACCEPTED\n")
                    success = True
                    break

                print("\n🔁 Retrying...\n")

                feedback = build_feedback(review["issues"])

                attempt += 1

            if not success:
                print("\n❌ FAILED AFTER RETRIES\n")

            print("\n" + "-" * 50)


if __name__ == "__main__":
    main()
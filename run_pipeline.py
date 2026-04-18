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
    """
    Convert reviewer issues → actionable instructions
    """

    instructions = "REVIEW FEEDBACK:\n"

    for issue in issues:
        if "Logic change" in issue:
            instructions += "- DO NOT change return values\n"
            instructions += "- Preserve original behavior exactly\n"

        if "Function call change" in issue:
            instructions += "- DO NOT change function calls\n"
            instructions += "- DO NOT add print/logging\n"

    instructions += "\nFix the code.\n"
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
        MAX_RETRIES = 2

        for query in queries:
            print(f"\n🔍 Query: {query}")

            selected_files = engine.query(query)
            context = builder.build_context(selected_files)

            attempt = 0
            success = False

            while attempt < MAX_RETRIES:

                # 🔥 UPDATED TASK
                result = executor.run(
                    context,
                    f"Refactor code WITHOUT changing behavior: {query}"
                )

                review = reviewer.review(context, result[0]["suggestion"])

                print("\n🤖 LLM OUTPUT:\n")
                print(result[0]["suggestion"])

                print("\n🔍 REVIEW RESULT:")
                print(review)

                if review["valid"]:
                    print("\n✅ ACCEPTED\n")
                    success = True
                    break

                print("\n🔁 Retrying...\n")

                # 🔥 STRONG FEEDBACK
                context.append({
                    "file": "REVIEW_FEEDBACK",
                    "code": build_feedback(review["issues"])
                })

                attempt += 1

            if not success:
                print("\n❌ FAILED AFTER RETRIES\n")

            print("\n" + "-" * 50)


if __name__ == "__main__":
    main()
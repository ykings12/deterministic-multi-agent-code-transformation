import os
import tempfile

from core.codebase_map import CodebaseMap
from planner.query_engine import QueryEngine
from planner.context_builder import ContextBuilder
from executor.executor import Executor
from planner.context_budget import ContextBudget
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
    print("🚀 Running Pipeline (Bigger Repo Test)...\n")

    with tempfile.TemporaryDirectory() as tmp:

        # -----------------------------
        # CREATE BIGGER REPO
        # -----------------------------

        # utils
        create_file(os.path.join(tmp, "utils.py"), """
def helper():
    return "hello"
""")

        # math
        create_file(os.path.join(tmp, "math_ops.py"), """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
""")

        # string utils
        create_file(os.path.join(tmp, "string_utils.py"), """
def format_text(s):
    return s.strip().lower()
""")

        # data processing
        create_file(os.path.join(tmp, "data_processor.py"), """
import utils
import string_utils

def process():
    text = utils.helper()
    return string_utils.format_text(text)
""")

        # service layer
        create_file(os.path.join(tmp, "service.py"), """
import data_processor

def serve():
    return data_processor.process()
""")

        # controller
        create_file(os.path.join(tmp, "controller.py"), """
import service

def handle_request():
    return service.serve()
""")

        # main
        create_file(os.path.join(tmp, "main.py"), """
import controller

def run():
    return controller.handle_request()
""")

        # unrelated file
        create_file(os.path.join(tmp, "logger.py"), """
def log(msg):
    print(msg)
""")

        create_file(os.path.join(tmp, "config.py"), """
DEBUG = True
""")

        # -----------------------------
        # BUILD SYSTEM
        # -----------------------------
        cb = CodebaseMap(tmp)
        code_map = cb.build()

        builder = ContextBuilder(code_map, tmp)
        executor = Executor(use_llm=True, debug=False)
        reviewer = Reviewer()

        queries = [
            "helper",
            "process data",
            "handle request",
            "add numbers"
        ]

        MAX_RETRIES = 3

        for query in queries:
            print(f"\n🔍 Query: {query}")

            budget = ContextBudget(code_map)

            selected_files = budget.select_top_k(query, k=2)

            print("📂 Selected Files:", selected_files)

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

            print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
import os
import tempfile

from core.codebase_map import CodebaseMap
from planner.context_builder import ContextBuilder
from planner.context_budget import ContextBudget
from planner.function_selector import FunctionSelector
from planner.planner import Planner
from executor.executor import Executor
from executor.step_executor import StepExecutor
from reviewer.reviewer import Reviewer
from editor.file_editor import FileEditor  # ✅ NEW


def create_file(path, content=""):
    with open(path, "w") as f:
        f.write(content)


def build_feedback(issues):
    """
    Convert reviewer issues into precise LLM instructions.
    """

    instructions = "\nREVIEW FEEDBACK:\n"

    for issue in issues:

        if "Invalid format" in issue:
            instructions += (
                "- Your previous response was correct BUT missing 'FILE:' headers.\n"
            )
            instructions += "- DO NOT change code, ONLY fix format.\n"

        elif "Duplicate file" in issue:
            instructions += "- You repeated the same file multiple times.\n"
            instructions += "- Output EACH file exactly once.\n"

        elif "Logic change" in issue:
            instructions += f"- You changed logic: {issue}\n"
            instructions += "- Revert to original logic EXACTLY.\n"

        elif "Function call change" in issue:
            instructions += "- Do NOT modify function calls.\n"

        elif "Unauthorized file" in issue:
            instructions += "- You modified a file not in context.\n"
            instructions += "- Only modify provided files.\n"

    instructions += "\nFix ALL issues WITHOUT introducing new ones.\n"

    return instructions


def main():
    print("🚀 Running Pipeline (Day 18 - Edit Layer Added)...\n")

    # with tempfile.TemporaryDirectory() as tmp:
    tmp = "./test_repo"
    os.makedirs(tmp, exist_ok=True)

        # -----------------------------
        # CREATE BIGGER REPO
        # -----------------------------
        create_file(
            os.path.join(tmp, "utils.py"),
            """
def helper():
    return "hello"
""",
        )

        create_file(
            os.path.join(tmp, "math_ops.py"),
            """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
""",
        )

        create_file(
            os.path.join(tmp, "string_utils.py"),
            """
def format_text(s):
    return s.strip().lower()
""",
        )

        create_file(
            os.path.join(tmp, "data_processor.py"),
            """
import utils
import string_utils

def process():
    text = utils.helper()
    return string_utils.format_text(text)
""",
        )

        create_file(
            os.path.join(tmp, "service.py"),
            """
import data_processor

def serve():
    return data_processor.process()
""",
        )

        create_file(
            os.path.join(tmp, "controller.py"),
            """
import service

def handle_request():
    return service.serve()
""",
        )

        create_file(
            os.path.join(tmp, "main.py"),
            """
import controller

def run():
    return controller.handle_request()
""",
        )

        create_file(
            os.path.join(tmp, "logger.py"),
            """
def log(msg):
    print(msg)
""",
        )

        create_file(
            os.path.join(tmp, "config.py"),
            """
DEBUG = True
""",
        )

        # -----------------------------
        # BUILD SYSTEM
        # -----------------------------
        cb = CodebaseMap(tmp)
        code_map = cb.build()

        builder = ContextBuilder(code_map, tmp)
        budget = ContextBudget(code_map)
        selector = FunctionSelector(code_map)

        executor = Executor(use_llm=True, debug=False)
        step_executor = StepExecutor(executor)
        planner = Planner(code_map)
        reviewer = Reviewer()
        editor = FileEditor(tmp)  # ✅ NEW

        queries = ["helper", "process data", "handle request", "add numbers"]

        MAX_RETRIES = 3

        # -----------------------------
        # PIPELINE LOOP
        # -----------------------------
        for query in queries:
            print(f"\n🔍 Query: {query}")

            # -----------------------------
            # STEP 1: Context Selection
            # -----------------------------
            selected_files = budget.select_top_k(query, k=1)
            print("📂 Selected Files:", selected_files)

            selected_functions = selector.select_functions(selected_files, query)

            if selected_functions:
                context = builder.build_function_context(selected_functions)
            else:
                context = builder.build_context(selected_files)

            print("\n📦 Context:\n", context)

            # -----------------------------
            # STEP 2: Planning
            # -----------------------------
            steps = planner.create_plan(query, selected_files)

            print("\n🧠 PLAN:")
            for step in steps:
                print(step)

            # -----------------------------
            # STEP 3: Execute Plan
            # -----------------------------
            for step in steps:
                print(f"\n🪜 STEP: {step}")

                attempt = 0
                success = False
                feedback = ""

                while attempt < MAX_RETRIES:

                    step_context = [c for c in context if c["file"] == step["target"]]

                    task = f"{step['type']} on {step['target']} WITHOUT changing behavior\n{feedback}"

                    output = step_executor.execute_step(step_context, step, task)

                    # -----------------------------
                    # NO-OP HANDLING
                    # -----------------------------
                    if not output.strip():
                        print("\n🤖 OUTPUT: (no changes)")
                        print("✅ STEP ACCEPTED\n")
                        success = True
                        break

                    review = reviewer.review(step_context, output)

                    print("\n🤖 STEP OUTPUT:\n", output)
                    print("\n🔍 REVIEW:", review)

                    if review["valid"]:
                        print("\n✅ STEP ACCEPTED\n")

                        # 🔥 APPLY CHANGES HERE
                        editor.apply_changes(output)

                        success = True
                        break

                    print("\n🔁 Retrying step...\n")

                    feedback = build_feedback(review["issues"])
                    attempt += 1

                if not success:
                    print("\n❌ STEP FAILED\n")
                    break

            print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

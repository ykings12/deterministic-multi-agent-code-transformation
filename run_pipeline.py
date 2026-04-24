from multiprocessing import context
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
from editor.patch_editor import PatchEditor
from planner.node_engine import NodeEngine


def create_file(path, content=""):
    with open(path, "w") as f:
        f.write(content)


def main():
    print("🚀 Running Pipeline (Day 19 - Strict Edit + Diff)...\n")

    with tempfile.TemporaryDirectory() as tmp:

        # -----------------------------
        # CREATE REPO
        # -----------------------------
        create_file(
            os.path.join(tmp, "utils.py"),
            """
def helper():
    return "hello"
""",
        )

        create_file(
            os.path.join(tmp, "data_processor.py"),
            """
import utils

def process():
    text = utils.helper()
    return text
""",
        )

        create_file(
            os.path.join(tmp, "controller.py"),
            """
import service

def handle_request():
    return service.serve_request()
""",
        )

        create_file(
            os.path.join(tmp, "math_ops.py"),
            """
def add(a, b):
    return a + b
""",
        )

        # -----------------------------
        # SYSTEM INIT
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
        editor = PatchEditor(tmp)

        queries = ["helper", "process data", "handle request", "add numbers"]
        # queries = ["rename helper"]

        # =========================================================
        # 🔥 NODE ENGINE
        # =========================================================

        def select_node(state):
            query = state["query"]

            selected_files = budget.select_top_k(query, k=3)
            state["selected_files"] = selected_files

            selected_functions = selector.select_functions(selected_files, query)

            # 🔥 ALWAYS include full file context
            context = builder.build_function_context(selected_functions)

            # Add missing files manually
            existing_files = {c["file"] for c in context}

            for f in selected_files:
                if f not in existing_files:
                    file_path = os.path.join(tmp, f)
                    with open(file_path, "r") as file:
                        code = file.read()

                    context.append({"file": f, "code": code, "functions": []})

            state["context"] = context

            print("📂 Selected Files:", selected_files)
            print("\n📦 Context:\n", context)

        def plan_node(state):
            if "rename" in state["query"].lower():
                print("❌ Rename operations are not supported (violates constraints)")
                return {"next": None}

            steps = planner.create_plan(state["query"], state["selected_files"])
            state["steps"] = steps
            state["step_index"] = 0

            print("\n🧠 PLAN:")
            for s in steps:
                print(s)

        def execute_node(state):
            step = state["steps"][state["step_index"]]
            context = state["context"]

            step_context = [c for c in context if c["file"] == step["target"]]

            # 🔥 FIX: ensure target file is always present
            if not step_context:
                print(f"⚠️ Missing context for {step['target']} → using fallback")
                step_context = context  # reuse existing context safely

            feedback = state.get("feedback", "")

            if step["type"] == "modify_function":
                task = (
                    f"Refactor function in {step['target']} WITHOUT changing behavior.\n"
                    f"- DO NOT rename the function\n"
                    f"- DO NOT change return values\n"
                    f"- ONLY minimal safe edits allowed\n"
                    f"{feedback}"
                )

            elif step["type"] == "update_usage":
                task = (
                    f"Update ONLY function calls in {step['target']}.\n"
                    f"STRICT RULES:\n"
                    f"- DO NOT modify function definitions\n"
                    f"- DO NOT create new functions\n"
                    f"- DO NOT rewrite the file\n"
                    f"- ONLY update existing function calls if needed\n"
                    f"- If no update needed → OUTPUT NOTHING\n"
                    f"{feedback}"
                )

            else:
                task = f"{step['type']} on {step['target']}\n{feedback}"

            output = step_executor.execute_step(step_context, step, task)

            state["last_output"] = output
            state["step_context"] = step_context

            print(f"\n🪜 STEP: {step}")
            print("\n🤖 OUTPUT:\n", output)

        def review_node(state):
            output = state["last_output"]
            context = state["step_context"]

            review = reviewer.review(context, output)
            state["last_review"] = review

            # 🔥 FIX: define issues BEFORE using it
            issues = review["issues"]

            # 🔥 early abort for repeated logic issues
            if any("Logic change" in i for i in issues):
                if state.get("retry_count", 0) >= 1:
                    print("❌ Repeated logic violation → aborting step")
                    return {"next": None}

            # 🔥 NO-OP OPTIMIZATION
            if output.strip():
                if output.strip() and context:
                    original_code = context[0]["code"].strip()
                if output.strip().endswith(original_code):
                    print("⚡ No meaningful change detected → skipping retries")
                    return {"next": "edit"}

            print("\n🔍 REVIEW:", review)

            # -----------------------------
            # INIT retry count
            # -----------------------------
            if "retry_count" not in state:
                state["retry_count"] = 0

            # -----------------------------
            # SUCCESS
            # -----------------------------
            if review["valid"]:
                state["retry_count"] = 0
                return {"next": "edit"}

            # -----------------------------
            # 🔥 INCREMENT RETRY COUNT
            # -----------------------------
            state["retry_count"] += 1
            print(f"🔁 Retry Count: {state['retry_count']}")

            # -----------------------------
            # FEEDBACK GENERATION
            # -----------------------------
            if any("Mixed FILE and EDIT" in i for i in issues):
                state["feedback"] = (
                    "CRITICAL FAILURE:\n"
                    "- You included FILE format which is FORBIDDEN.\n"
                    "- OUTPUT MUST CONTAIN ONLY EDIT block.\n"
                    "- DO NOT include FILE under any condition.\n"
                )

            elif any("Must use EDIT format" in i for i in issues):
                state["feedback"] = "CRITICAL: Use EDIT format ONLY. Do NOT use FILE."

            elif any("Invalid format" in i for i in issues):
                state["feedback"] = "Fix format only. Do NOT change code."

            elif any("Logic change" in i for i in issues):
                state["feedback"] = (
                    "CRITICAL:\n"
                    "- You modified logic which is STRICTLY forbidden.\n"
                    "- Restore EXACT original return values.\n"
                    "- DO NOT change constants, strings, or expressions.\n"
                    "- Output SAME function with ZERO logical changes.\n"
                )

            else:
                state["feedback"] = "Fix issues: " + str(issues)

            # -----------------------------
            # MAX RETRY
            # -----------------------------
            if state["retry_count"] >= 3:
                print("\n❌ MAX RETRIES REACHED")
                return {"next": None}

            return {"next": "execute"}

        def edit_node(state):
            output = state["last_output"]

            editor.apply_patch(output)

            print("\n💾 Changes Applied")

            state["step_index"] += 1

            if state["step_index"] >= len(state["steps"]):
                return {"next": None}

            return {"next": "execute"}

        # -----------------------------
        # GRAPH
        # -----------------------------
        engine = NodeEngine()

        engine.add_node("select", select_node)
        engine.add_node("plan", plan_node)
        engine.add_node("execute", execute_node)
        engine.add_node("review", review_node)
        engine.add_node("edit", edit_node)

        engine.add_edge("select", "plan")
        engine.add_edge("plan", "execute")
        engine.add_edge("execute", "review")
        engine.add_edge("review", "edit")

        # -----------------------------
        # RUN
        # -----------------------------
        for query in queries:
            print(f"\n🔍 Query: {query}")

            state = {"query": query}
            engine.run("select", state)

            print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

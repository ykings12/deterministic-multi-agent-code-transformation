from typing import Dict, Any, List


class WorkflowState:
    def __init__(self, query: str):
        self.query = query
        self.selected_files: List[str] = []
        self.context: List[Dict] = []
        self.steps: List[Dict] = []
        self.current_step: Dict = {}
        self.output: str = ""
        self.review: Dict = {}
        self.feedback: str = ""
        self.success: bool = False

        # 🔥 Existing
        self.retry_count: int = 0
        self.error_type: str = ""

        # 🔥 NEW (Day 20)
        self.confidence: int = 0


class Workflow:
    def __init__(
        self,
        budget,
        selector,
        builder,
        planner,
        step_executor,
        reviewer,
        editor,
    ):
        self.budget = budget
        self.selector = selector
        self.builder = builder
        self.planner = planner
        self.step_executor = step_executor
        self.reviewer = reviewer
        self.editor = editor

    # =========================================================
    # NODE 1: CONTEXT SELECTION
    # =========================================================
    def select_context(self, state: WorkflowState):
        state.selected_files = self.budget.select_top_k(state.query, k=1)

        selected_functions = self.selector.select_functions(
            state.selected_files, state.query
        )

        if selected_functions:
            state.context = self.builder.build_function_context(selected_functions)
        else:
            state.context = self.builder.build_context(state.selected_files)

        print("📂 Selected Files:", state.selected_files)
        print("\n📦 Context:\n", state.context)

        return state

    # =========================================================
    # NODE 2: PLANNING
    # =========================================================
    def plan(self, state: WorkflowState):
        state.steps = self.planner.create_plan(state.query, state.selected_files)

        print("\n🧠 PLAN:")
        for step in state.steps:
            print(step)

        return state

    # =========================================================
    # NODE 3: EXECUTE STEP
    # =========================================================
    def execute_step(self, state: WorkflowState):
        step = state.current_step

        step_context = [c for c in state.context if c["file"] == step["target"]]

        task = f"{step['type']} on {step['target']} WITHOUT changing behavior\n{state.feedback}"

        state.output = self.step_executor.execute_step(step_context, step, task)

        print("\n🤖 STEP OUTPUT:\n", state.output)

        return state

    # =========================================================
    # ERROR CLASSIFIER
    # =========================================================
    def classify_error(self, state: WorkflowState):
        issues = state.review.get("issues", [])

        if not issues:
            state.error_type = ""
            return state

        issue_text = " ".join(issues).lower()

        if "format" in issue_text:
            state.error_type = "format"
        elif "logic" in issue_text:
            state.error_type = "logic"
        elif "syntax" in issue_text:
            state.error_type = "syntax"
        else:
            state.error_type = "unknown"

        return state

    # =========================================================
    # NODE 4: REVIEW
    # =========================================================
    def review(self, state: WorkflowState):
        step = state.current_step

        step_context = [c for c in state.context if c["file"] == step["target"]]

        if not state.output.strip():
            print("\n🤖 OUTPUT: (no changes)")
            state.success = True
            state.confidence = 2  # 🔥 treat no-op as high confidence
            return state

        state.review = self.reviewer.review(step_context, state.output)

        print("\n🔍 REVIEW:", state.review)

        state.success = state.review["valid"]

        # 🔥 CONFIDENCE
        state.confidence = state.review["score"]

        print(f"🎯 Confidence: {state.confidence}")

        if state.confidence >= 2:
            print("✅ High confidence output")

        state = self.classify_error(state)

        print(f"⚠️ Error Type: {state.error_type}")

        return state

    # =========================================================
    # SMART RETRY HANDLER
    # =========================================================
    def handle_retry(self, state: WorkflowState):
        state.retry_count += 1

        print(f"\n🔁 Retry Count: {state.retry_count}")

        # 🔥 SMART FEEDBACK
        if state.error_type == "format":
            state.feedback = "Fix ONLY format. Use EDIT format correctly."

        elif state.error_type == "logic":
            state.feedback = "Revert logic. DO NOT change behavior."

        elif state.error_type == "syntax":
            state.feedback = "Fix syntax errors ONLY."

        else:
            state.feedback = "Fix issues: " + str(state.review["issues"])

        print("🧠 Feedback:", state.feedback)

        return state

    # =========================================================
    # APPLY
    # =========================================================
    def apply(self, state: WorkflowState):
        if state.success:
            print("\n🔷 NODE: edit")
            self.editor.apply_patch(state.output)
            print("\n💾 Changes Applied")

        return state

    # =========================================================
    # MAIN RUN
    # =========================================================
    def run(self, query: str):
        print(f"\n🔍 Query: {query}")

        state = WorkflowState(query)

        state = self.select_context(state)
        state = self.plan(state)

        for step in state.steps:
            print(f"\n🪜 STEP: {step}")

            state.current_step = step
            state.retry_count = 0
            state.feedback = ""

            MAX_RETRIES = 3

            while state.retry_count < MAX_RETRIES:

                state = self.execute_step(state)
                state = self.review(state)

                # 🔥 DAY 20 CORE LOGIC
                if state.success:
                    state = self.apply(state)
                    break

                # 🔥 LOW CONFIDENCE → retry
                if state.confidence <= 1:
                    print("\n🔷 NODE: retry")
                    state = self.handle_retry(state)
                    continue

                # 🔥 HIGH CONFIDENCE BUT INVALID (rare case)
                print("\n⚠️ Unexpected state → forcing retry")
                state = self.handle_retry(state)

            if not state.success:
                print("\n❌ STEP FAILED")
                break

from typing import Dict, Any, List


class WorkflowState:
    """
    Central state shared across all nodes.

    This is the CORE of LangGraph-style design.
    """

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
        """
        LangGraph-style workflow engine.

        Nodes:
        → select_context
        → plan
        → execute_step
        → review
        → apply
        """

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
    # NODE 4: REVIEW
    # =========================================================
    def review(self, state: WorkflowState):
        step = state.current_step

        step_context = [c for c in state.context if c["file"] == step["target"]]

        if not state.output.strip():
            print("\n🤖 OUTPUT: (no changes)")
            state.success = True
            return state

        state.review = self.reviewer.review(step_context, state.output)

        print("\n🔍 REVIEW:", state.review)

        state.success = state.review["valid"]

        return state

    # =========================================================
    # NODE 5: APPLY CHANGES
    # =========================================================
    def apply(self, state: WorkflowState):
        if state.success:
            print("\n✅ APPLYING CHANGES")
            self.editor.apply_changes(state.output)

        return state

    # =========================================================
    # MAIN RUN FUNCTION
    # =========================================================
    def run(self, query: str):
        print(f"\n🔍 Query: {query}")

        state = WorkflowState(query)

        # Step 1: context
        state = self.select_context(state)

        # Step 2: plan
        state = self.plan(state)

        # Step 3: execute steps
        for step in state.steps:
            print(f"\n🪜 STEP: {step}")

            state.current_step = step
            attempt = 0
            MAX_RETRIES = 3

            while attempt < MAX_RETRIES:

                state = self.execute_step(state)
                state = self.review(state)

                if state.success:
                    state = self.apply(state)
                    break

                print("\n🔁 Retrying...\n")
                state.feedback = str(state.review["issues"])
                attempt += 1

            if not state.success:
                print("\n❌ STEP FAILED")
                break

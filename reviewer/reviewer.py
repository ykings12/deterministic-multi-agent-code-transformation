import ast
from typing import Dict, List


class Reviewer:
    def __init__(self, debug: bool = False):
        """
        Reviewer validates LLM output.

        Acts as SAFETY LAYER between LLM and system.
        Ensures:
        → Correct format
        → No syntax errors
        → No logic/behavior changes
        → No unauthorized file modifications
        """

        self.debug = debug

    def review(self, original_context: List[Dict], llm_output: str) -> Dict:
        issues = []
        score = 0

        # -----------------------------
        # ✅ NO-OP CHECK (ADD HERE)
        # -----------------------------
        if not llm_output.strip():
            return self._result(True, 1, [])

        # -----------------------------
        # 1. FORMAT CHECK
        # -----------------------------
        if not llm_output.strip().startswith("FILE:"):
            issues.append("Invalid format: Missing FILE header")
            return self._result(False, score, issues)

        score += 1

        # -----------------------------
        # 2. PARSE OUTPUT
        # -----------------------------
        try:
            files = self._parse_output(llm_output)
        except ValueError as e:
            issues.append(str(e))
            return self._result(False, score, issues)

        if not files:
            issues.append("No files parsed from output")
            return self._result(False, score, issues)

        # -----------------------------
        # 3. VALIDATE FILE SCOPE
        # -----------------------------
        allowed_files = {item["file"] for item in original_context}

        for file_name in files.keys():
            if file_name not in allowed_files:
                issues.append(f"Unauthorized file modification: {file_name}")

        # -----------------------------
        # 4. SYNTAX CHECK
        # -----------------------------
        for file_name, code in files.items():
            if not code.strip():
                issues.append(f"Empty code in {file_name}")
                continue

            try:
                ast.parse(code)
                score += 1
            except SyntaxError:
                issues.append(f"Syntax error in {file_name}")

        # -----------------------------
        # 5. LOGIC + BEHAVIOR CHECK
        # -----------------------------
        for item in original_context:
            file_name = item["file"]
            original_code = item["code"]
            new_code = files.get(file_name)

            # If file not modified → skip
            if not new_code:
                continue

            if self._major_change(original_code, new_code):
                issues.append(f"Logic change detected in {file_name}")

            if self._call_change(original_code, new_code):
                issues.append(f"Function call change in {file_name}")

        return self._result(len(issues) == 0, score, issues)

    # =========================================================
    # HELPERS
    # =========================================================

    def _parse_output(self, output: str) -> Dict[str, str]:
        """
        Parse LLM output into:
        file → code

        Also detects duplicate file outputs.
        """

        files = {}
        current_file = None
        code_lines = []
        seen_files = set()

        for line in output.split("\n"):
            if line.startswith("FILE:"):
                if current_file:
                    if current_file in seen_files:
                        raise ValueError(f"Duplicate file output: {current_file}")

                    files[current_file] = "\n".join(code_lines).strip()
                    seen_files.add(current_file)

                current_file = line.replace("FILE:", "").strip()
                code_lines = []
            else:
                code_lines.append(line)

        if current_file:
            if current_file in seen_files:
                raise ValueError(f"Duplicate file output: {current_file}")

            files[current_file] = "\n".join(code_lines).strip()

        return files

    def _major_change(self, old: str, new: str) -> bool:
        """
        Improved logic check:
        → Avoid false positives for equivalent code
        """

        try:
            old_tree = ast.parse(old)
            new_tree = ast.parse(new)
        except Exception:
            return True

        # ✅ Exact match after normalization → safe
        if self._normalize_code(old) == self._normalize_code(new):
            return False

        # ✅ Compare sorted returns (fix false positives)
        if sorted(self._extract_returns(old_tree)) != sorted(self._extract_returns(new_tree)):
            return True

        # ✅ Compare function names (structure)
        if self._extract_functions(old_tree) != self._extract_functions(new_tree):
            return True

        return False


    def _call_change(self, old: str, new: str) -> bool:
        """
        Detect function call changes (side effects)
        """

        try:
            old_tree = ast.parse(old)
            new_tree = ast.parse(new)
        except Exception:
            return True

        return self._extract_calls(old_tree) != self._extract_calls(new_tree)

    # -----------------------------
    # AST EXTRACTORS
    # -----------------------------

    def _extract_returns(self, tree):
        return [
            ast.dump(node.value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Return) and node.value
        ]

    def _extract_calls(self, tree):
        calls = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)

        return sorted(calls)

    def _extract_functions(self, tree):
        return sorted([
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ])

    # -----------------------------
    # NORMALIZATION
    # -----------------------------

    def _normalize_code(self, code: str) -> str:
        """
        Normalize code to avoid false positives
        """
        return "\n".join(
            line.strip()
            for line in code.splitlines()
            if line.strip()
        )

    # -----------------------------
    # FINAL RESULT
    # -----------------------------

    def _result(self, valid: bool, score: int, issues: List[str]) -> Dict:
        if self.debug:
            print("\n[REVIEW DEBUG]")
            print("Valid:", valid)
            print("Score:", score)
            print("Issues:", issues)

        return {
            "valid": valid,
            "score": score,
            "issues": issues
        }
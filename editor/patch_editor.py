import ast
import os
from typing import Dict
import difflib


class PatchEditor:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def apply_patch(self, output: str):
        output = output.strip()

        has_file = "FILE:" in output
        has_edit = "EDIT:" in output

        # ❌ HARD FAIL (no silent fixing anymore)
        if has_file and has_edit:
            print("❌ Mixed FILE + EDIT format — REJECTED")
            return

        if output.startswith("EDIT:"):
            self._apply_structured_edit(output)
        else:
            self._fallback_full_write(output)

    # -----------------------------
    # 🔥 STRUCTURED EDIT
    # -----------------------------
    def _apply_structured_edit(self, output: str):
        lines = output.splitlines()

        file_name = ""
        target = ""
        code_lines = []
        mode = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("EDIT:"):
                file_name = stripped.replace("EDIT:", "").strip()

            elif stripped.startswith("TARGET:"):
                target = stripped.replace("TARGET:", "").strip()

            elif stripped.startswith("CODE:"):
                mode = True

            elif mode:
                code_lines.append(line)

        if not file_name or not target or not code_lines:
            print("❌ Invalid EDIT format")
            return

        self._replace_function(file_name, target, "\n".join(code_lines))

    # -----------------------------
    # 🔥 FUNCTION REPLACEMENT + DIFF
    # -----------------------------
    def _replace_function(self, file_name: str, func_name: str, new_code: str):
        file_path = os.path.join(self.repo_path, file_name)

        with open(file_path, "r") as f:
            old_source = f.read()

        tree = ast.parse(old_source)
        lines = old_source.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                start = node.lineno - 1
                end = node.end_lineno

                new_lines = new_code.strip().splitlines()
                updated = lines[:start] + new_lines + lines[end:]

                new_source = "\n".join(updated)

                # 🔥 DIFF PRINT
                print("\n🔍 DIFF:")
                for line in difflib.unified_diff(
                    old_source.splitlines(), new_source.splitlines(), lineterm=""
                ):
                    print(line)

                with open(file_path, "w") as f:
                    f.write(new_source)

                print(f"\n🧩 Patched function '{func_name}' in {file_name}")
                return

    # -----------------------------
    # 🔁 FALLBACK
    # -----------------------------
    def _fallback_full_write(self, output: str):
        parts = output.split("FILE:")

        for part in parts:
            if not part.strip():
                continue

            lines = part.strip().split("\n")
            file_name = lines[0].strip()
            code = "\n".join(lines[1:])

            file_path = os.path.join(self.repo_path, file_name)

            with open(file_path, "r") as f:
                old_code = f.read()

            print("\n🔍 DIFF:")
            for line in difflib.unified_diff(
                old_code.splitlines(), code.splitlines(), lineterm=""
            ):
                print(line)

            with open(file_path, "w") as f:
                f.write(code)

            print(f"\n💾 Full write: {file_name}")

from typing import List, Dict


class Executor:
    def __init__(self):
        """
        Executor simulates LLM behavior.

        NOTE:
        → We mock LLM for now
        → Later we plug real API (Groq/Gemini)
        """
        pass

    def run(self, context: List[Dict], task: str) -> List[Dict]:
        """
        Generate code improvements.

        Input:
        - context → selected files
        - task → user instruction

        Output:
        [
            {
                "file": "...",
                "suggestion": "..."
            }
        ]
        """

        results = []

        for item in context:
            file_name = item["file"]

            suggestion = self._mock_llm(item["code"], task)

            results.append({
                "file": file_name,
                "suggestion": suggestion
            })

        return results

    def _mock_llm(self, code: str, task: str) -> str:
        """
        Simulated LLM output.

        WHY?
        → No API dependency yet
        → Test system pipeline
        """

        return f"Improve code for task: {task}"
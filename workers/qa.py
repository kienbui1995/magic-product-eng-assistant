import os
from magic_ai_sdk import Worker
from llm import complete_json, is_configured

worker = Worker(name="QA", endpoint="http://localhost:9004")

SYSTEM = """You are a senior QA engineer. Given a spec and/or code diff, produce a JSON object with:
- "mode": the testing mode (generate/reproduce/verify)
- "test_cases": array of 3-5 test cases, each with "name", "steps", "expected"
- "checklist": array of 3-5 QA checklist items"""

MOCK = lambda spec, mode: {
    "mode": mode,
    "test_cases": [f"Verify behavior described in spec: {spec[:80]}..."],
    "checklist": ["Unit tests pass", "Integration tests pass", "No regressions"],
}


@worker.capability("qa_testing", description="Generates test cases and checklists from spec and code diff")
def test(spec: str = "", code_diff: str = "", mode: str = "generate") -> dict:
    if not is_configured():
        return MOCK(spec, mode)
    result = complete_json(SYSTEM, f"Mode: {mode}\nSpec:\n{spec}\n\nCode diff:\n{code_diff}")
    return result or MOCK(spec, mode)


if __name__ == "__main__":
    server = os.getenv("MAGIC_SERVER", "http://localhost:8080")
    worker.register(server)
    worker.serve(port=9004)

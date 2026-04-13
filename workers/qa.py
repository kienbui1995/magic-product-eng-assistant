from magic_ai_sdk import Worker

worker = Worker(name="QA", endpoint="http://localhost:9004")


@worker.capability("qa_testing", description="Generates test cases and checklists from spec and code diff")
def test(spec: str = "", code_diff: str = "", mode: str = "generate") -> dict:
    # TODO: integrate with LLM
    return {
        "mode": mode,
        "test_cases": [f"Verify behavior described in spec: {spec[:80]}..."],
        "checklist": ["Unit tests pass", "Integration tests pass", "No regressions"],
    }


if __name__ == "__main__":
    worker.register("http://localhost:8080")
    worker.serve(port=9004)

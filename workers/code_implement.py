import os
from magic_ai_sdk import Worker
from llm import complete_json, is_configured

worker = Worker(name="CodeImplement", endpoint="http://localhost:9003")

SYSTEM = """You are a senior software engineer. Given a design doc, produce a JSON object with:
- "suggestions": array of 3-5 implementation suggestions with file paths and descriptions
- "pr_diff": a unified diff string showing the key code changes"""

MOCK = lambda design: {
    "suggestions": [f"Implement module based on design: {design[:100]}..."],
    "pr_diff": "diff --git a/main.py b/main.py\n+# new implementation placeholder",
}


@worker.capability("code_implementation", description="Generates code suggestions and PR diffs from a design doc")
def implement(design: str, repo: str = "") -> dict:
    if not is_configured():
        return MOCK(design)
    result = complete_json(SYSTEM, f"Design:\n{design}\n\nRepo context:\n{repo}")
    return result or MOCK(design)


if __name__ == "__main__":
    server = os.getenv("MAGIC_SERVER", "http://localhost:8080")
    worker.register(server)
    worker.serve(port=9003)

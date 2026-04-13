from magic_ai_sdk import Worker

worker = Worker(name="CodeImplement", endpoint="http://localhost:9003")


@worker.capability("code_implementation", description="Generates code suggestions and PR diffs from a design doc")
def implement(design: str, repo: str = "") -> dict:
    # TODO: integrate with LLM
    return {
        "suggestions": [f"Implement module based on design: {design[:100]}..."],
        "pr_diff": "diff --git a/main.py b/main.py\n+# new implementation placeholder",
    }


if __name__ == "__main__":
    worker.register("http://localhost:8080")
    worker.serve(port=9003)

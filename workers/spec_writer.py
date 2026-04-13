from magic_ai_sdk import Worker

worker = Worker(name="SpecWriter", endpoint="http://localhost:9001")


@worker.capability("spec_writing", description="Generates PRD drafts, user stories, and acceptance criteria from a feature idea")
def write_spec(idea: str, context: str = "") -> dict:
    # TODO: integrate with LLM
    return {
        "prd": f"# PRD: {idea}\n\n## Context\n{context}\n\n## Requirements\n- TBD",
        "user_stories": [f"As a user, I want {idea} so that I can benefit from it."],
        "acceptance_criteria": ["Given the feature is enabled, when user interacts, then expected outcome occurs."],
    }


if __name__ == "__main__":
    worker.register("http://localhost:8080")
    worker.serve(port=9001)

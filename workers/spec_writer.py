import os
from magic_ai_sdk import Worker
from llm import complete_json, is_configured

worker = Worker(name="SpecWriter", endpoint="http://localhost:9001")

SYSTEM = """You are a senior product manager. Given a feature idea and context, produce a JSON object with:
- "prd": a markdown PRD document with sections: Overview, Problem, Solution, Requirements, Success Metrics
- "user_stories": array of 3-5 user stories in "As a..., I want..., so that..." format
- "acceptance_criteria": array of 3-5 testable acceptance criteria"""

MOCK = lambda idea, ctx: {
    "prd": f"# PRD: {idea}\n\n## Context\n{ctx}\n\n## Requirements\n- TBD",
    "user_stories": [f"As a user, I want {idea} so that I can benefit from it."],
    "acceptance_criteria": ["Given the feature is enabled, when user interacts, then expected outcome occurs."],
}


@worker.capability("spec_writing", description="Generates PRD drafts, user stories, and acceptance criteria from a feature idea")
def write_spec(idea: str, context: str = "") -> dict:
    if not is_configured():
        return MOCK(idea, context)
    result = complete_json(SYSTEM, f"Feature idea: {idea}\nContext: {context}")
    return result or MOCK(idea, context)


if __name__ == "__main__":
    server = os.getenv("MAGIC_SERVER", "http://localhost:8080")
    worker.register(server)
    worker.serve(port=9001)

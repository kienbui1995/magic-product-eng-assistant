import os
from magic_ai_sdk import Worker
from llm import complete_json, is_configured

worker = Worker(name="TechDesign", endpoint="http://localhost:9002")

SYSTEM = """You are a senior software architect. Given a PRD, produce a JSON object with:
- "hld": a markdown high-level design document with sections: Architecture, Components, Data Flow, Tech Stack
- "modules": array of 3-5 module names with brief descriptions
- "risks": array of 2-3 technical risks"""

MOCK = lambda prd: {
    "hld": f"# High-Level Design\n\nBased on PRD:\n{prd[:200]}...",
    "modules": ["api-layer", "business-logic", "data-store"],
    "risks": ["Scope creep", "Third-party API dependency"],
}


@worker.capability("tech_design", description="Produces HLD, module decomposition, and risk analysis from a PRD")
def design(prd: str, architecture: str = "") -> dict:
    if not is_configured():
        return MOCK(prd)
    result = complete_json(SYSTEM, f"PRD:\n{prd}\n\nExisting architecture:\n{architecture}")
    return result or MOCK(prd)


if __name__ == "__main__":
    server = os.getenv("MAGIC_SERVER", "http://localhost:8080")
    worker.register(server)
    worker.serve(port=9002)

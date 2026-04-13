from magic_ai_sdk import Worker

worker = Worker(name="TechDesign", endpoint="http://localhost:9002")


@worker.capability("tech_design", description="Produces HLD, module decomposition, and risk analysis from a PRD")
def design(prd: str, architecture: str = "") -> dict:
    # TODO: integrate with LLM
    return {
        "hld": f"# High-Level Design\n\nBased on PRD:\n{prd[:200]}...",
        "modules": ["api-layer", "business-logic", "data-store"],
        "risks": ["Scope creep", "Third-party API dependency"],
    }


if __name__ == "__main__":
    worker.register("http://localhost:8080")
    worker.serve(port=9002)

import os
from magic_ai_sdk import Worker
from llm import complete_json, is_configured

worker = Worker(name="ReleaseNotes", endpoint="http://localhost:9005")

SYSTEM = """You are a technical writer. Given a changelog or merged PRs, produce a JSON object with:
- "release_notes": a markdown release notes document with sections: What's New, Bug Fixes, Breaking Changes"""

MOCK = lambda changelog, prs: {
    "release_notes": f"## What's New\n\n- Changes based on: {changelog[:100] or prs[:100]}...",
}


@worker.capability("release_notes", description="Generates release notes from merged PRs and changelog")
def generate(changelog: str = "", merged_prs: str = "") -> dict:
    if not is_configured():
        return MOCK(changelog, merged_prs)
    result = complete_json(SYSTEM, f"Changelog:\n{changelog}\n\nMerged PRs:\n{merged_prs}")
    return result or MOCK(changelog, merged_prs)


if __name__ == "__main__":
    server = os.getenv("MAGIC_SERVER", "http://localhost:8080")
    worker.register(server)
    worker.serve(port=9005)

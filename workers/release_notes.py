from magic_ai_sdk import Worker

worker = Worker(name="ReleaseNotes", endpoint="http://localhost:9005")


@worker.capability("release_notes", description="Generates release notes from merged PRs and changelog")
def generate(changelog: str = "", merged_prs: str = "") -> dict:
    # TODO: integrate with LLM
    return {
        "release_notes": f"## What's New\n\n- Changes based on: {changelog[:100] or merged_prs[:100]}...",
    }


if __name__ == "__main__":
    worker.register("http://localhost:8080")
    worker.serve(port=9005)

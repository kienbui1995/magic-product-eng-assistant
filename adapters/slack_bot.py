"""Slack bot adapter — forwards /magic commands to MagiC workflow API."""
import json
import os

import httpx
from slack_bolt import App

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)

MAGIC_URL = os.environ.get("MAGIC_SERVER", "http://localhost:8080")


@app.command("/magic")
def handle_magic(ack, command, respond):
    ack()
    text = command.get("text", "")

    if text.startswith("feature-launch "):
        idea = text.removeprefix("feature-launch ").strip()
        wf = httpx.post(f"{MAGIC_URL}/api/v1/workflows", json={
            "name": f"Feature: {idea}",
            "steps": [
                {"id": "spec", "task_type": "spec_writing", "input": {"idea": idea, "context": ""}},
                {"id": "design", "task_type": "tech_design", "depends_on": ["spec"], "input": {"prd": ""}},
                {"id": "code", "task_type": "code_implementation", "depends_on": ["design"], "input": {"design": ""}},
                {"id": "qa", "task_type": "qa_testing", "depends_on": ["design"], "input": {"spec": ""}},
                {"id": "release", "task_type": "release_notes", "depends_on": ["code", "qa"], "input": {"changelog": ""}},
            ],
        }, timeout=10).json()
        respond(f"🚀 Workflow started: `{wf['id']}`\nTrack: {MAGIC_URL}/api/v1/workflows/{wf['id']}")
    else:
        respond("Usage: `/magic feature-launch <your feature idea>`")


if __name__ == "__main__":
    app.start(port=3000)

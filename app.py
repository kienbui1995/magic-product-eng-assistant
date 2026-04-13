import json
import time
import streamlit as st
import requests

st.set_page_config(page_title="Magic Product Assistant", page_icon="🪄", layout="wide")
st.title("🪄 Magic Product Assistant")

# --- Sidebar ---
with st.sidebar:
    server_url = st.text_input("MagiC Server URL", value="http://localhost:8080")
    try:
        r = requests.get(f"{server_url}/health", timeout=2)
        st.success("🟢 Connected" if r.ok else "🟡 Server responded with error")
    except requests.ConnectionError:
        st.warning("🔴 Cannot reach server")

STEP_EMOJI = {"completed": "✅", "running": "🔄", "pending": "⏳", "failed": "❌"}

FEATURE_WORKFLOW = {
    "name": "Feature Delivery",
    "steps": [
        {"id": "spec", "task_type": "spec_writing", "input": {}},
        {"id": "design", "task_type": "tech_design", "depends_on": ["spec"], "input": {}},
        {"id": "code", "task_type": "code_implementation", "depends_on": ["design"], "input": {}},
        {"id": "qa", "task_type": "qa_testing", "depends_on": ["design"], "input": {}},
        {"id": "release", "task_type": "release_notes", "depends_on": ["code", "qa"], "input": {}},
    ],
}

BUG_WORKFLOW = {
    "name": "Bug Lifecycle",
    "steps": [
        {"id": "reproduce", "task_type": "qa_testing", "input": {}},
        {"id": "fix", "task_type": "code_implementation", "depends_on": ["reproduce"], "input": {}},
        {"id": "verify", "task_type": "qa_testing", "depends_on": ["fix"], "input": {}},
    ],
}


def submit_and_poll(workflow: dict):
    """Submit workflow and poll for completion."""
    try:
        resp = requests.post(f"{server_url}/api/v1/workflows", json=workflow, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to submit workflow: {e}")
        return

    wf = resp.json()
    wf_id = wf.get("id", "unknown")
    st.info(f"Workflow submitted — ID: `{wf_id}`")

    progress = st.empty()
    while True:
        try:
            poll = requests.get(f"{server_url}/api/v1/workflows/{wf_id}", timeout=5).json()
        except requests.RequestException:
            st.warning("Lost connection while polling…")
            break

        status = poll.get("status", "unknown")
        steps = poll.get("steps", [])

        with progress.container():
            st.write(f"**Workflow status:** {status}")
            for s in steps:
                emoji = STEP_EMOJI.get(s.get("status", "pending"), "⏳")
                st.write(f"{emoji} **{s.get('id', '?')}** — {s.get('status', 'pending')}")

        if status in ("completed", "failed"):
            break
        time.sleep(2)

    # Show step outputs
    for s in steps:
        output = s.get("output")
        if output:
            with st.expander(f"Output: {s.get('id', '?')}"):
                st.json(output) if isinstance(output, dict) else st.text(str(output))


# --- Tabs ---
tab_feature, tab_bug = st.tabs(["Feature Delivery", "Bug Lifecycle"])

with tab_feature:
    idea = st.text_input("Feature Idea", placeholder="e.g. Add dark mode to dashboard")
    context = st.text_input("Context / Repo", placeholder="e.g. frontend repo, React + Tailwind")
    if st.button("🚀 Launch Feature Workflow", key="feat"):
        wf = json.loads(json.dumps(FEATURE_WORKFLOW))
        wf["steps"][0]["input"] = {"idea": idea, "context": context}
        submit_and_poll(wf)

with tab_bug:
    bug_desc = st.text_input("Bug Description", placeholder="e.g. Login page crashes on Safari")
    repro = st.text_input("Steps to Reproduce", placeholder="e.g. 1. Open Safari 2. Click Login")
    if st.button("🐛 Launch Bug Workflow", key="bug"):
        wf = json.loads(json.dumps(BUG_WORKFLOW))
        wf["steps"][0]["input"] = {"spec": bug_desc, "mode": "reproduce", "repro_steps": repro}
        submit_and_poll(wf)

# --- Bottom: Workers & Costs ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("Workers")
    try:
        workers = requests.get(f"{server_url}/api/v1/workers", timeout=3).json()
        if isinstance(workers, list) and workers:
            for w in workers:
                st.write(f"• **{w.get('name', '?')}** — {w.get('status', '?')} — `{', '.join(w.get('capabilities', []))}`")
        else:
            st.caption("No workers registered.")
    except requests.RequestException:
        st.caption("Could not fetch workers.")

with col2:
    st.subheader("Cost Report")
    try:
        costs = requests.get(f"{server_url}/api/v1/costs", timeout=3).json()
        st.json(costs)
    except requests.RequestException:
        st.caption("Could not fetch cost report.")

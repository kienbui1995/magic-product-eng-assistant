import json
import time
import streamlit as st
import requests

st.set_page_config(page_title="Magic Product Assistant", page_icon="🪄", layout="wide")
st.title("🪄 Magic Product Assistant")


def generate_mock_output(task_type: str, user_input: dict) -> dict:
    idea = user_input.get("idea", user_input.get("spec", "the feature"))
    context = user_input.get("context", "the project")
    if task_type == "spec_writing":
        return {
            "prd_title": f"PRD: {idea}",
            "summary": f"Implement {idea} within {context}.",
            "user_stories": [
                f"As a user, I want {idea} so that I can be more productive.",
                f"As an admin, I want to configure {idea} settings.",
                f"As a developer, I want {idea} to be well-documented.",
            ],
            "acceptance_criteria": [
                f"{idea} is functional and accessible.",
                "Unit and integration tests pass with >80% coverage.",
                "Performance benchmarks meet SLA requirements.",
            ],
        }
    if task_type == "tech_design":
        return {
            "hld_title": f"Technical Design: {idea}",
            "modules": [
                {"name": "API Layer", "description": f"REST endpoints for {idea}"},
                {"name": "Business Logic", "description": f"Core logic implementing {idea}"},
                {"name": "Data Layer", "description": "Database schema changes and migrations"},
            ],
            "risks": [
                {"risk": "Backward compatibility", "mitigation": "Feature flag rollout"},
                {"risk": "Performance regression", "mitigation": "Load testing before release"},
            ],
        }
    if task_type == "code_implementation":
        return {
            "pr_title": f"feat: {idea}",
            "files_changed": 7,
            "insertions": 342,
            "deletions": 28,
            "diff_summary": f"Implemented {idea} with new endpoints, service layer, and tests.",
        }
    if task_type == "qa_testing":
        return {
            "test_cases": [
                {"name": "Happy path", "status": "passed", "description": f"Verify {idea} works end-to-end"},
                {"name": "Edge case — empty input", "status": "passed", "description": "Handles empty/null inputs gracefully"},
                {"name": "Load test", "status": "passed", "description": "Handles 100 concurrent requests within SLA"},
            ],
            "coverage": "87%",
        }
    if task_type == "release_notes":
        return {
            "version": "1.4.0",
            "date": "2026-04-13",
            "highlights": [f"New: {idea}", "Improved test coverage to 87%", "Bug fixes and performance improvements"],
        }
    return {"result": f"Completed {task_type}"}


# --- Sidebar ---
PROVIDERS = {
    "None (mock data)": ("", "", ""),
    "OpenAI": ("https://api.openai.com/v1", "gpt-4o-mini", "sk-..."),
    "Google Gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "gemini-2.0-flash", "AIza..."),
    "Groq": ("https://api.groq.com/openai/v1", "llama-3.3-70b-versatile", "gsk_..."),
    "OpenRouter": ("https://openrouter.ai/api/v1", "google/gemma-3-27b-it:free", "sk-or-..."),
    "Ollama (local)": ("http://localhost:11434/v1", "llama3", "ollama"),
    "Custom": ("", "", ""),
}

with st.sidebar:
    demo_mode = st.toggle("Demo Mode (no server needed)", value=True)
    if demo_mode:
        st.success("🟢 Demo Mode — no server needed")
        server_url = ""
    else:
        server_url = st.text_input("MagiC Server URL", value="http://localhost:8080")
        try:
            r = requests.get(f"{server_url}/health", timeout=2)
            st.success("🟢 Connected" if r.ok else "🟡 Server responded with error")
        except requests.ConnectionError:
            st.warning("🔴 Cannot reach server")

    st.divider()
    st.subheader("🤖 LLM Settings (BYOK)")
    provider = st.selectbox("Provider", list(PROVIDERS.keys()))
    default_url, default_model, key_hint = PROVIDERS[provider]

    if provider == "None (mock data)":
        st.caption("Workers will return mock data.")
        llm_key, llm_url, llm_model = "", "", ""
    else:
        llm_key = st.text_input("API Key", type="password", placeholder=key_hint)
        if provider == "Custom":
            llm_url = st.text_input("Base URL (OpenAI-compatible)", placeholder="https://your-provider.com/v1")
            llm_model = st.text_input("Model", placeholder="model-name")
        else:
            llm_url = default_url
            llm_model = st.text_input("Model", value=default_model)
        if llm_key:
            st.success(f"🟢 LLM: {provider} / {llm_model}")
        else:
            st.caption("Enter API key to enable LLM. Workers use mock data without it.")

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


def generate_llm_output(task_type: str, user_input: dict) -> dict:
    """Call LLM via OpenAI-compatible API. Returns empty dict on failure."""
    if not llm_key:
        return {}
    prompts = {
        "spec_writing": ("You are a senior PM. Write a PRD as JSON with keys: prd_title, summary, user_stories (array), acceptance_criteria (array).", f"Feature: {user_input}"),
        "tech_design": ("You are a senior architect. Write a technical design as JSON with keys: hld_title, modules (array of {{name, description}}), risks (array of {{risk, mitigation}}).", f"PRD: {user_input}"),
        "code_implementation": ("You are a senior engineer. Write implementation plan as JSON with keys: pr_title, files_changed, insertions, deletions, diff_summary.", f"Design: {user_input}"),
        "qa_testing": ("You are a senior QA. Write test plan as JSON with keys: test_cases (array of {{name, status, description}}), coverage.", f"Spec: {user_input}"),
        "release_notes": ("You are a tech writer. Write release notes as JSON with keys: version, date, highlights (array).", f"Changes: {user_input}"),
    }
    sys_prompt, user_prompt = prompts.get(task_type, ("Respond as JSON.", str(user_input)))
    try:
        from openai import OpenAI
        client = OpenAI(api_key=llm_key, base_url=llm_url,
                        default_headers={"HTTP-Referer": "https://magic-team-assistant.streamlit.app",
                                         "X-Title": "Magic Product Assistant"})
        resp = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": sys_prompt + "\nRespond ONLY with valid JSON."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(raw)
    except Exception as e:
        st.warning(f"LLM error: {e}. Falling back to mock data.")
        return {}


def simulate_workflow(workflow: dict):
    """Simulate workflow execution locally with mock or LLM data."""
    steps = workflow["steps"]
    user_input = steps[0].get("input", {})
    progress = st.empty()

    for i, step in enumerate(steps):
        # Show current progress
        with progress.container():
            st.write(f"**Workflow status:** running")
            for j, s in enumerate(steps):
                if j < i:
                    st.write(f"✅ **{s['id']}** — completed")
                elif j == i:
                    st.write(f"🔄 **{s['id']}** — running")
                else:
                    st.write(f"⏳ **{s['id']}** — pending")
        time.sleep(1.5)
        step["output"] = generate_llm_output(step["task_type"], user_input) or generate_mock_output(step["task_type"], user_input)
        step["status"] = "completed"

    # Final state
    with progress.container():
        st.write(f"**Workflow status:** completed")
        for s in steps:
            st.write(f"✅ **{s['id']}** — completed")

    for s in steps:
        with st.expander(f"Output: {s['id']}"):
            st.json(s["output"])


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


def run_workflow(workflow: dict):
    if demo_mode:
        simulate_workflow(workflow)
    else:
        submit_and_poll(workflow)


# --- Tabs ---
tab_feature, tab_bug = st.tabs(["Feature Delivery", "Bug Lifecycle"])

with tab_feature:
    idea = st.text_input("Feature Idea", placeholder="e.g. Add dark mode to dashboard")
    context = st.text_input("Context / Repo", placeholder="e.g. frontend repo, React + Tailwind")
    if st.button("🚀 Launch Feature Workflow", key="feat"):
        wf = json.loads(json.dumps(FEATURE_WORKFLOW))
        wf["steps"][0]["input"] = {"idea": idea, "context": context}
        run_workflow(wf)

with tab_bug:
    bug_desc = st.text_input("Bug Description", placeholder="e.g. Login page crashes on Safari")
    repro = st.text_input("Steps to Reproduce", placeholder="e.g. 1. Open Safari 2. Click Login")
    if st.button("🐛 Launch Bug Workflow", key="bug"):
        wf = json.loads(json.dumps(BUG_WORKFLOW))
        wf["steps"][0]["input"] = {"spec": bug_desc, "mode": "reproduce", "repro_steps": repro}
        run_workflow(wf)

# --- Bottom: Workers & Costs ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("Workers")
    if demo_mode:
        for name, caps in [("SpecWriter", "spec_writing"), ("TechDesign", "tech_design"), ("CodeImplement", "code_implementation"), ("QA", "qa_testing"), ("ReleaseNotes", "release_notes")]:
            st.write(f"• **{name}** — active — `{caps}`")
    else:
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
    if demo_mode:
        st.json({"total_cost": 0.42, "task_count": 5})
    else:
        try:
            costs = requests.get(f"{server_url}/api/v1/costs", timeout=3).json()
            st.json(costs)
        except requests.RequestException:
            st.caption("Could not fetch cost report.")

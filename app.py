import json, time, random
import streamlit as st
import requests

st.set_page_config(page_title="MagiC — AI Worker Management", page_icon="🪄", layout="wide")

# ── Custom CSS for better visuals ────────────────────────────────────────────
st.markdown("""<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea11, #764ba211);
        border: 1px solid #667eea33;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; font-weight: 600; }
    [data-testid="stMetricValue"] { font-size: 1.6rem; }
    [data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fa;
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    div[data-testid="stProgress"] > div > div > div {
        border-radius: 8px;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa, #ffffff);
    }
</style>""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
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
    st.image("https://img.shields.io/badge/MagiC-v0.7.0-6C5CE7?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCI+PHRleHQgeT0iMjAiIGZvbnQtc2l6ZT0iMjAiPvCfqpQ8L3RleHQ+PC9zdmc+")
    demo_mode = st.toggle("Demo Mode (no server needed)", value=True)
    if demo_mode:
        st.success("🟢 Demo Mode")
        server_url = ""
    else:
        server_url = st.text_input("MagiC Server URL", value="http://localhost:8080")
        try:
            r = requests.get(f"{server_url}/health", timeout=2)
            st.success("🟢 Connected") if r.ok else st.warning("🟡 Error")
        except Exception:
            st.error("🔴 Cannot reach server")

    st.divider()
    st.subheader("🤖 LLM (BYOK)")
    provider = st.selectbox("Provider", list(PROVIDERS.keys()))
    default_url, default_model, key_hint = PROVIDERS[provider]
    llm_key = llm_url = llm_model = ""
    if provider != "None (mock data)":
        llm_key = st.text_input("API Key", type="password", placeholder=key_hint)
        if provider == "Custom":
            llm_url = st.text_input("Base URL", placeholder="https://your-provider.com/v1")
            llm_model = st.text_input("Model", placeholder="model-name")
        else:
            llm_url = default_url
            llm_model = st.text_input("Model", value=default_model)
        if llm_key:
            st.success(f"🟢 {provider}")

    st.divider()
    st.caption("Built with [MagiC](https://github.com/kienbui1995/magic) — Kubernetes for AI Agents")

# ── Mock Data ────────────────────────────────────────────────────────────────
MOCK_WORKERS = [
    {"id": "w_001", "name": "SpecWriter", "status": "active", "capabilities": [{"name": "spec_writing", "est_cost_per_call": 0.05}], "current_load": 1, "limits": {"max_concurrent_tasks": 5, "max_cost_per_day": 10.0}, "total_cost_today": 0.15, "team_id": "team_product", "tags": {"lang": "en", "domain": "product"}, "session_mode": "stateless"},
    {"id": "w_002", "name": "TechDesign", "status": "active", "capabilities": [{"name": "tech_design", "est_cost_per_call": 0.08}], "current_load": 0, "limits": {"max_concurrent_tasks": 5, "max_cost_per_day": 10.0}, "total_cost_today": 0.08, "team_id": "team_eng", "tags": {"lang": "en", "domain": "engineering"}, "session_mode": "stateless"},
    {"id": "w_003", "name": "CodeImplement", "status": "active", "capabilities": [{"name": "code_implementation", "est_cost_per_call": 0.12}], "current_load": 2, "limits": {"max_concurrent_tasks": 5, "max_cost_per_day": 15.0}, "total_cost_today": 0.36, "team_id": "team_eng", "tags": {"lang": "en", "domain": "engineering"}, "session_mode": "stateless"},
    {"id": "w_004", "name": "QA", "status": "active", "capabilities": [{"name": "qa_testing", "est_cost_per_call": 0.04}], "current_load": 0, "limits": {"max_concurrent_tasks": 10, "max_cost_per_day": 5.0}, "total_cost_today": 0.12, "team_id": "team_qa", "tags": {"lang": "en", "domain": "quality"}, "session_mode": "stateless"},
    {"id": "w_005", "name": "ReleaseNotes", "status": "active", "capabilities": [{"name": "release_notes", "est_cost_per_call": 0.02}], "current_load": 0, "limits": {"max_concurrent_tasks": 5, "max_cost_per_day": 3.0}, "total_cost_today": 0.02, "team_id": "team_product", "tags": {"lang": "en", "domain": "product"}, "session_mode": "stateless"},
    {"id": "w_006", "name": "CheapBot", "status": "paused", "capabilities": [{"name": "spec_writing", "est_cost_per_call": 0.01}], "current_load": 0, "limits": {"max_concurrent_tasks": 3, "max_cost_per_day": 1.0}, "total_cost_today": 1.02, "team_id": "team_product", "tags": {"lang": "en"}, "session_mode": "stateless"},
]

MOCK_TEAMS = [
    {"id": "team_product", "name": "Product Team", "org_id": "org_acme", "workers": ["w_001", "w_005", "w_006"], "daily_budget": 20.0},
    {"id": "team_eng", "name": "Engineering Team", "org_id": "org_acme", "workers": ["w_002", "w_003"], "daily_budget": 30.0},
    {"id": "team_qa", "name": "QA Team", "org_id": "org_acme", "workers": ["w_004"], "daily_budget": 10.0},
]

MOCK_POLICIES = [
    {"id": "pol_001", "name": "Production Guardrails", "org_id": "org_acme", "enabled": True, "rules": [
        {"name": "allowed_capabilities", "effect": "hard", "value": ["spec_writing", "tech_design", "code_implementation", "qa_testing", "release_notes"]},
        {"name": "max_cost_per_task", "effect": "soft", "value": 1.0},
        {"name": "max_timeout_ms", "effect": "hard", "value": 60000},
        {"name": "blocked_capabilities", "effect": "hard", "value": ["shell_exec", "file_delete"]},
    ]},
]

MOCK_ROLES = [
    {"id": "rb_001", "org_id": "org_acme", "subject": "alice@acme.com", "role": "owner"},
    {"id": "rb_002", "org_id": "org_acme", "subject": "bob@acme.com", "role": "admin"},
    {"id": "rb_003", "org_id": "org_acme", "subject": "carol@acme.com", "role": "viewer"},
]

MOCK_KNOWLEDGE = [
    {"id": "kb_001", "title": "API Design Standards", "content": "All APIs must follow REST conventions...", "tags": ["api", "standards"], "scope": "org"},
    {"id": "kb_002", "title": "Release Process", "content": "1. Create branch 2. PR review 3. CI pass 4. Deploy to staging...", "tags": ["release", "process"], "scope": "org"},
    {"id": "kb_003", "title": "Testing Guidelines", "content": "Minimum 80% coverage. E2E tests for critical paths...", "tags": ["testing", "qa"], "scope": "team"},
]

# ── LLM Helper ───────────────────────────────────────────────────────────────
def call_llm(system_prompt: str, user_prompt: str) -> str:
    if not llm_key:
        return ""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=llm_key, base_url=llm_url,
                        default_headers={"HTTP-Referer": "https://magic-team-assistant.streamlit.app", "X-Title": "MagiC Demo"})
        resp = client.chat.completions.create(model=llm_model,
            messages=[{"role": "system", "content": system_prompt + "\nRespond ONLY with valid JSON."},
                      {"role": "user", "content": user_prompt}], temperature=0.7)
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(raw)
    except Exception as e:
        st.warning(f"LLM error: {e}")
        return {}

def mock_output(task_type, idea="feature"):
    m = {
        "spec_writing": {"prd": f"# PRD: {idea}", "user_stories": [f"As a user, I want {idea}"], "acceptance_criteria": ["Feature works end-to-end"]},
        "tech_design": {"hld": f"# Design: {idea}", "modules": ["API", "Service", "DB"], "risks": ["Scope creep"]},
        "code_implementation": {"pr_title": f"feat: {idea}", "files_changed": 7, "diff_summary": f"Implemented {idea}"},
        "qa_testing": {"test_cases": [{"name": "Happy path", "status": "passed"}], "coverage": "87%"},
        "release_notes": {"version": "1.4.0", "highlights": [f"New: {idea}"]},
    }
    return m.get(task_type, {"result": "done"})

def get_output(task_type, user_input):
    prompts = {
        "spec_writing": ("Senior PM. JSON: prd, user_stories[], acceptance_criteria[]", f"Feature: {user_input}"),
        "tech_design": ("Senior architect. JSON: hld, modules[], risks[]", f"PRD: {user_input}"),
        "code_implementation": ("Senior engineer. JSON: pr_title, files_changed, diff_summary", f"Design: {user_input}"),
        "qa_testing": ("Senior QA. JSON: test_cases[{{name,status,description}}], coverage", f"Spec: {user_input}"),
        "release_notes": ("Tech writer. JSON: version, highlights[]", f"Changes: {user_input}"),
    }
    sys, usr = prompts.get(task_type, ("JSON.", str(user_input)))
    return call_llm(sys, usr) or mock_output(task_type, str(user_input)[:50])

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🪄 MagiC — AI Worker Management")
st.caption("Don't build another AI. Manage the ones you have. • [GitHub](https://github.com/kienbui1995/magic) • [Docs](https://kienbui1995.github.io/magic/docs/)")

# Top metrics
m1, m2, m3, m4, m5 = st.columns(5)
active = sum(1 for w in MOCK_WORKERS if w["status"] == "active")
total_cost = sum(w["total_cost_today"] for w in MOCK_WORKERS)
m1.metric("Workers", f"{active}/{len(MOCK_WORKERS)}", "active")
m2.metric("Teams", len(MOCK_TEAMS))
m3.metric("Cost Today", f"${total_cost:.2f}", f"budget: ${sum(t['daily_budget'] for t in MOCK_TEAMS):.0f}")
m4.metric("Policies", len(MOCK_POLICIES), "1 active")
m5.metric("Knowledge", len(MOCK_KNOWLEDGE), "entries")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_wf, tab_workers, tab_routing, tab_policy, tab_cost, tab_kb, tab_arch = st.tabs(
    ["🔄 Workflows", "🤖 Workers", "🧭 Routing", "🛡️ Policies & RBAC", "💰 Cost Control", "📚 Knowledge", "🏗️ Architecture"])

# ── Tab 1: Workflows ─────────────────────────────────────────────────────────
with tab_wf:
    st.subheader("DAG Workflow Orchestration")
    st.caption("MagiC executes steps in dependency order. Independent steps run in parallel.")

    c1, c2 = st.columns([2, 1])
    with c2:
        st.markdown("**Feature Delivery DAG:**")
        st.code("""    spec
     │
   design
   ╱    ╲
 code    qa    ← parallel
   ╲    ╱
  release""", language=None)

        st.markdown("**Bug Lifecycle DAG:**")
        st.code("""reproduce → fix → verify""", language=None)

    with c1:
        wf_type = st.radio("Workflow", ["Feature Delivery", "Bug Lifecycle"], horizontal=True)
        if wf_type == "Feature Delivery":
            idea = st.text_input("Feature Idea", placeholder="e.g. Add dark mode to dashboard", key="wf_idea")
            context = st.text_area("Context", placeholder="Tech stack, repo, constraints...", height=68, key="wf_ctx")
            steps_def = [
                {"id": "spec", "task_type": "spec_writing"},
                {"id": "design", "task_type": "tech_design", "depends_on": ["spec"]},
                {"id": "code", "task_type": "code_implementation", "depends_on": ["design"]},
                {"id": "qa", "task_type": "qa_testing", "depends_on": ["design"]},
                {"id": "release", "task_type": "release_notes", "depends_on": ["code", "qa"]},
            ]
            user_input = {"idea": idea, "context": context}
        else:
            bug = st.text_input("Bug Description", placeholder="e.g. Login crashes on Safari", key="wf_bug")
            steps_def = [
                {"id": "reproduce", "task_type": "qa_testing"},
                {"id": "fix", "task_type": "code_implementation", "depends_on": ["reproduce"]},
                {"id": "verify", "task_type": "qa_testing", "depends_on": ["fix"]},
            ]
            user_input = {"spec": bug, "mode": "reproduce"}

        if st.button("🚀 Launch Workflow", type="primary"):
            progress = st.empty()
            outputs = {}
            for i, step in enumerate(steps_def):
                with progress.container():
                    cols = st.columns(len(steps_def))
                    for j, s in enumerate(steps_def):
                        emoji = "✅" if j < i else ("🔄" if j == i else "⏳")
                        cols[j].markdown(f"**{emoji} {s['id']}**")
                time.sleep(1.0 if not llm_key else 0.3)
                outputs[step["id"]] = get_output(step["task_type"], user_input)

            with progress.container():
                cols = st.columns(len(steps_def))
                for j, s in enumerate(steps_def):
                    cols[j].markdown(f"**✅ {s['id']}**")
            st.success(f"Workflow completed — {len(steps_def)} steps, trace_id: `trace_{random.randint(1000,9999)}`")
            for sid, out in outputs.items():
                with st.expander(f"📄 Output: {sid}", expanded=(sid == "spec")):
                    st.json(out)

# ── Tab 2: Workers ───────────────────────────────────────────────────────────
with tab_workers:
    st.subheader("Worker Fleet")
    st.caption("Workers register capabilities, MagiC routes tasks to the best match.")

    for w in MOCK_WORKERS:
        status_color = "🟢" if w["status"] == "active" else "🟡" if w["status"] == "paused" else "🔴"
        cap_names = ", ".join(c["name"] for c in w["capabilities"])
        cost_pct = (w["total_cost_today"] / w["limits"]["max_cost_per_day"] * 100) if w["limits"]["max_cost_per_day"] > 0 else 0

        with st.expander(f"{status_color} **{w['name']}** — `{cap_names}` — load: {w['current_load']}/{w['limits']['max_concurrent_tasks']}", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.metric("Status", w["status"])
            c2.metric("Cost Today", f"${w['total_cost_today']:.2f}", f"{cost_pct:.0f}% of budget")
            c3.metric("Session Mode", w.get("session_mode", "stateless"))
            st.json({"id": w["id"], "team": w["team_id"], "tags": w.get("tags", {}),
                      "capabilities": w["capabilities"], "limits": w["limits"]})

# ── Tab 3: Routing ───────────────────────────────────────────────────────────
with tab_routing:
    st.subheader("Capability-Based Routing")
    st.caption("MagiC routes tasks to workers based on strategy. Try different strategies below.")

    cap = st.selectbox("Required Capability", ["spec_writing", "tech_design", "code_implementation", "qa_testing", "release_notes"])
    strategy = st.selectbox("Routing Strategy", ["best_match", "cheapest", "specific"])

    candidates = [w for w in MOCK_WORKERS if any(c["name"] == cap for c in w["capabilities"]) and w["status"] == "active"]

    if not candidates:
        st.warning("No active workers with this capability.")
    else:
        st.markdown(f"**{len(candidates)} candidate(s):**")
        if strategy == "best_match":
            scored = sorted(candidates, key=lambda w: 1 - w["current_load"] / max(w["limits"]["max_concurrent_tasks"], 1), reverse=True)
            winner = scored[0]
            st.info(f"🏆 **{winner['name']}** selected — highest availability ({winner['limits']['max_concurrent_tasks'] - winner['current_load']} slots free)")
        elif strategy == "cheapest":
            scored = sorted(candidates, key=lambda w: min(c["est_cost_per_call"] for c in w["capabilities"] if c["name"] == cap))
            winner = scored[0]
            cost = min(c["est_cost_per_call"] for c in winner["capabilities"] if c["name"] == cap)
            st.info(f"🏆 **{winner['name']}** selected — lowest cost (${cost:.2f}/call)")
        else:
            winner = candidates[0]
            st.info(f"🏆 **{winner['name']}** selected — specific worker")

        for w in candidates:
            is_winner = w["id"] == winner["id"]
            prefix = "→ " if is_winner else "  "
            avail = w["limits"]["max_concurrent_tasks"] - w["current_load"]
            cost = min(c["est_cost_per_call"] for c in w["capabilities"] if c["name"] == cap)
            st.text(f"{prefix}{'🏆' if is_winner else '  '} {w['name']:15s}  load={w['current_load']}/{w['limits']['max_concurrent_tasks']}  avail={avail}  cost=${cost:.2f}")

# ── Tab 4: Policies & RBAC ──────────────────────────────────────────────────
with tab_policy:
    pc1, pc2 = st.columns(2)

    with pc1:
        st.subheader("🛡️ Policy Engine")
        st.caption("Hard guardrails reject. Soft guardrails warn + audit.")
        for p in MOCK_POLICIES:
            st.markdown(f"**{p['name']}** {'🟢 enabled' if p['enabled'] else '⚪ disabled'}")
            for rule in p["rules"]:
                icon = "🚫" if rule["effect"] == "hard" else "⚠️"
                st.text(f"  {icon} {rule['name']}: {rule['value']}")

        st.divider()
        st.markdown("**Test a policy guardrail:**")
        test_cap = st.text_input("Capability to test", value="shell_exec", key="pol_test")
        test_cost = st.number_input("Task max_cost ($)", value=0.5, key="pol_cost")
        if st.button("Test Policy", key="pol_btn"):
            violations = []
            for p in MOCK_POLICIES:
                if not p["enabled"]:
                    continue
                for rule in p["rules"]:
                    if rule["name"] == "blocked_capabilities" and test_cap in rule["value"]:
                        violations.append({"rule": rule["name"], "effect": rule["effect"], "message": f"'{test_cap}' is blocked"})
                    if rule["name"] == "allowed_capabilities" and test_cap not in rule["value"]:
                        violations.append({"rule": rule["name"], "effect": rule["effect"], "message": f"'{test_cap}' not in whitelist"})
                    if rule["name"] == "max_cost_per_task" and test_cost > rule["value"]:
                        violations.append({"rule": rule["name"], "effect": rule["effect"], "message": f"cost ${test_cost} > limit ${rule['value']}"})
            if violations:
                hard = [v for v in violations if v["effect"] == "hard"]
                soft = [v for v in violations if v["effect"] == "soft"]
                if hard:
                    st.error(f"🚫 REJECTED — {len(hard)} hard violation(s)")
                if soft:
                    st.warning(f"⚠️ WARNING — {len(soft)} soft violation(s)")
                st.json(violations)
            else:
                st.success("✅ ALLOWED — no policy violations")

    with pc2:
        st.subheader("🔐 RBAC")
        st.caption("Role-based access: owner > admin > viewer")
        perms = {"owner": ["read", "write", "delete", "admin"], "admin": ["read", "write", "delete"], "viewer": ["read"]}
        st.markdown("**Permission Matrix:**")
        header = "| Role | read | write | delete | admin |\n|------|------|-------|--------|-------|\n"
        for role, acts in perms.items():
            row = f"| {role} | " + " | ".join("✅" if a in acts else "❌" for a in ["read", "write", "delete", "admin"]) + " |"
            header += row + "\n"
        st.markdown(header)

        st.divider()
        st.markdown("**Role Bindings (org_acme):**")
        for rb in MOCK_ROLES:
            icon = "👑" if rb["role"] == "owner" else "🔧" if rb["role"] == "admin" else "👁️"
            st.text(f"  {icon} {rb['subject']:25s} → {rb['role']}")

# ── Tab 5: Cost Control ─────────────────────────────────────────────────────
with tab_cost:
    st.subheader("Budget Tracking & Auto-Pause")
    st.caption("MagiC warns at 80% budget and auto-pauses workers at 100%.")

    for w in MOCK_WORKERS:
        budget = w["limits"]["max_cost_per_day"]
        spent = w["total_cost_today"]
        pct = (spent / budget * 100) if budget > 0 else 0
        bar_color = "normal" if pct < 80 else ("off" if pct >= 100 else "normal")

        c1, c2 = st.columns([3, 1])
        with c1:
            label = f"{w['name']} — ${spent:.2f} / ${budget:.2f}"
            if pct >= 100:
                label += " 🚫 AUTO-PAUSED"
            elif pct >= 80:
                label += " ⚠️ WARNING"
            st.progress(min(pct / 100, 1.0), text=label)
        with c2:
            st.metric("", f"{pct:.0f}%")

    st.divider()
    st.markdown("**Organization Cost Report:**")
    total = sum(w["total_cost_today"] for w in MOCK_WORKERS)
    budget_total = sum(t["daily_budget"] for t in MOCK_TEAMS)
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Total Spent", f"${total:.2f}")
    rc2.metric("Total Budget", f"${budget_total:.2f}")
    rc3.metric("Remaining", f"${budget_total - total:.2f}")

    st.markdown("**Per-Team Breakdown:**")
    for team in MOCK_TEAMS:
        team_workers = [w for w in MOCK_WORKERS if w["team_id"] == team["id"]]
        team_cost = sum(w["total_cost_today"] for w in team_workers)
        st.text(f"  {team['name']:20s}  ${team_cost:.2f} / ${team['daily_budget']:.2f}  ({len(team_workers)} workers)")

# ── Tab 6: Knowledge Hub ────────────────────────────────────────────────────
with tab_kb:
    st.subheader("Shared Knowledge Base")
    st.caption("Workers share context via the Knowledge Hub. Supports keyword + semantic (pgvector) search.")

    search = st.text_input("🔍 Search knowledge", placeholder="e.g. testing guidelines", key="kb_search")
    results = MOCK_KNOWLEDGE
    if search:
        results = [k for k in MOCK_KNOWLEDGE if search.lower() in k["title"].lower() or search.lower() in k["content"].lower() or any(search.lower() in t for t in k["tags"])]

    for k in results:
        with st.expander(f"📄 {k['title']} — tags: {', '.join(k['tags'])} — scope: {k['scope']}"):
            st.markdown(k["content"])

    st.divider()
    st.markdown("**Add Knowledge Entry:**")
    kb_title = st.text_input("Title", key="kb_title")
    kb_content = st.text_area("Content", height=80, key="kb_content")
    kb_tags = st.text_input("Tags (comma-separated)", key="kb_tags")
    if st.button("Add Entry", key="kb_add") and kb_title:
        MOCK_KNOWLEDGE.append({"id": f"kb_{random.randint(100,999)}", "title": kb_title, "content": kb_content, "tags": [t.strip() for t in kb_tags.split(",")], "scope": "org"})
        st.success(f"Added: {kb_title}")
        st.rerun()

# ── Tab 7: Architecture ─────────────────────────────────────────────────────
with tab_arch:
    st.subheader("MagiC Architecture")
    st.code("""
                ┌──────────────────────────────────────────────┐
                │              MagiC Core (Go)                 │
                ├──────────────────────────────────────────────┤
  HTTP Request ─>  Gateway (auth, RBAC, rate limit, policy)    │
                │    │                                         │
                │    v                                         │
                │  Router ──> Registry (find best worker)      │
                │    │          │                               │
                │    v          v                               │
                │  Dispatcher ──> Worker A (HTTP POST)         │
                │    │              Worker B                    │
                │    │              Worker C                    │
                │    v                                         │
                │  Orchestrator (multi-step DAG workflows)     │
                │  Evaluator (output quality validation)       │
                │  Cost Controller (budget tracking)           │
                │  Policy Engine (hard/soft guardrails)        │
                │  RBAC (owner/admin/viewer)                   │
                │  Org Manager (teams, policies)               │
                │  Knowledge Hub (shared context + pgvector)   │
                │  Monitor (events, metrics, logging)          │
                └──────────────────────────────────────────────┘
    """, language=None)

    st.markdown("**Plugin System** — extend any component:")
    plugins = {
        "Router": "Strategy interface — add custom routing logic (round-robin, priority, geo-aware)",
        "Evaluator": "EvalPlugin interface — add custom output validation (LLM judge, regex, schema)",
        "Cost Controller": "CostPolicy interface — add custom budget rules (per-task cap, team quotas)",
        "Monitor": "LogSink interface — add custom log destinations (Datadog, Loki, S3)",
    }
    for name, desc in plugins.items():
        st.markdown(f"- **{name}** — {desc}")

    st.divider()
    st.markdown("**Tech Stack:**")
    tc1, tc2, tc3, tc4 = st.columns(4)
    tc1.markdown("🔵 **Core:** Go 1.25+")
    tc2.markdown("🟡 **SDK:** Python, Go, TypeScript")
    tc3.markdown("🟢 **Storage:** Memory / SQLite / PostgreSQL")
    tc4.markdown("📊 **Observability:** Prometheus + JSON logs")

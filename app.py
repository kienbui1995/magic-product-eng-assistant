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
    {"id": "w_001", "name": "SpecWriter", "status": "active", "framework": "🐍 LangChain", "capabilities": [{"name": "spec_writing", "est_cost_per_call": 0.05}], "current_load": 1, "limits": {"max_concurrent_tasks": 5, "max_cost_per_day": 10.0}, "total_cost_today": 0.15, "team_id": "team_product", "tags": {"lang": "en", "domain": "product"}, "session_mode": "stateless"},
    {"id": "w_002", "name": "TechDesign", "status": "active", "framework": "🦜 CrewAI", "capabilities": [{"name": "tech_design", "est_cost_per_call": 0.08}], "current_load": 0, "limits": {"max_concurrent_tasks": 5, "max_cost_per_day": 10.0}, "total_cost_today": 0.08, "team_id": "team_eng", "tags": {"lang": "en", "domain": "engineering"}, "session_mode": "stateless"},
    {"id": "w_003", "name": "CodeImplement", "status": "active", "framework": "📘 TypeScript SDK", "capabilities": [{"name": "code_implementation", "est_cost_per_call": 0.12}], "current_load": 2, "limits": {"max_concurrent_tasks": 5, "max_cost_per_day": 15.0}, "total_cost_today": 0.36, "team_id": "team_eng", "tags": {"lang": "en", "domain": "engineering"}, "session_mode": "stateless"},
    {"id": "w_004", "name": "QA", "status": "active", "framework": "🔵 Go SDK", "capabilities": [{"name": "qa_testing", "est_cost_per_call": 0.04}], "current_load": 0, "limits": {"max_concurrent_tasks": 10, "max_cost_per_day": 5.0}, "total_cost_today": 0.12, "team_id": "team_qa", "tags": {"lang": "en", "domain": "quality"}, "session_mode": "stateless"},
    {"id": "w_005", "name": "ReleaseNotes", "status": "active", "framework": "🐍 Python SDK", "capabilities": [{"name": "release_notes", "est_cost_per_call": 0.02}], "current_load": 0, "limits": {"max_concurrent_tasks": 5, "max_cost_per_day": 3.0}, "total_cost_today": 0.02, "team_id": "team_product", "tags": {"lang": "en", "domain": "product"}, "session_mode": "stateless"},
    {"id": "w_006", "name": "CheapBot", "status": "paused", "framework": "🐍 Python SDK", "capabilities": [{"name": "spec_writing", "est_cost_per_call": 0.01}], "current_load": 0, "limits": {"max_concurrent_tasks": 3, "max_cost_per_day": 1.0}, "total_cost_today": 1.02, "team_id": "team_product", "tags": {"lang": "en"}, "session_mode": "stateless"},
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
    {"id": "kb_001", "title": "API Design Standards", "tags": ["api", "standards"], "scope": "org",
     "content": """## API Design Standards (v2.1)

**Base URL:** All APIs use `/api/v1/` prefix. Version in URL, not headers.

**Naming:** Use plural nouns (`/users`, `/tasks`). Nest sub-resources: `/orgs/{id}/teams`.

**Methods:** GET (read), POST (create), PUT (full update), PATCH (partial), DELETE (remove).

**Responses:** Always return JSON. Include `id`, `created_at`, `updated_at`. Errors: `{"error": "message", "code": 400}`.

**Pagination:** `?limit=100&offset=0`. Response includes `total_count`. Max limit: 1000.

**Auth:** Bearer token in `Authorization` header. 401 for missing/invalid, 403 for insufficient permissions."""},
    {"id": "kb_002", "title": "Release Process", "tags": ["release", "process", "deployment"], "scope": "org",
     "content": """## Release Process

1. **Branch** — Create `release/vX.Y.Z` from `main`
2. **Changelog** — Update CHANGELOG.md following Keep a Changelog format
3. **PR Review** — Minimum 2 approvals. CI must pass (tests + lint + security scan)
4. **Tag** — `git tag vX.Y.Z` triggers release workflow
5. **Staging** — Auto-deploy to staging. Smoke test for 30 minutes
6. **Production** — Manual approval gate. Rolling deploy with health checks
7. **Monitor** — Watch error rates for 1 hour post-deploy. Rollback if >1% error rate increase

**Versioning:** Semantic versioning. Breaking changes = major bump. New features = minor. Fixes = patch."""},
    {"id": "kb_003", "title": "Testing Guidelines", "tags": ["testing", "qa", "coverage"], "scope": "team",
     "content": """## Testing Guidelines

**Coverage Targets:** Unit ≥ 85%, Integration ≥ 70%, E2E covers top 10 user flows.

**Unit Tests:** Test business logic in isolation. Mock external dependencies. Fast (<100ms each).

**Integration Tests:** Test API endpoints with real DB (test container). Verify request/response contracts.

**E2E Tests:** Playwright for critical user journeys. Run nightly + before release.

**Performance Tests:** k6 load tests for new endpoints. Baseline: <100ms p95 for reads, <500ms for writes.

**Security Tests:** OWASP ZAP scan on every PR. Dependency audit weekly (Snyk/Dependabot)."""},
    {"id": "kb_004", "title": "Incident Response Playbook", "tags": ["incident", "ops", "runbook"], "scope": "org",
     "content": """## Incident Response

**Severity Levels:**
- **P0** (Critical): Service down. All hands. Resolve <1h. Postmortem required.
- **P1** (High): Major feature broken. On-call + backup. Resolve <4h.
- **P2** (Medium): Degraded performance. Next business day.

**Steps:** Detect → Triage → Communicate → Fix → Verify → Postmortem

**Communication:** P0/P1: Slack #incidents + status page update within 15 min. Stakeholder update every 30 min."""},
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
        "spec_writing": {
            "prd": f"# PRD: {idea}\n\n## Problem Statement\nUsers have repeatedly requested {idea}. Current workarounds are manual and error-prone, leading to ~30% drop-off in the affected user flow.\n\n## Proposed Solution\nImplement {idea} as a first-class feature with full CRUD support, real-time sync, and backward compatibility with existing workflows.\n\n## Success Metrics\n- 20% increase in feature adoption within 30 days\n- <200ms p95 latency for all new endpoints\n- Zero data migration issues",
            "user_stories": [
                f"As a **power user**, I want {idea} so that I can complete my workflow 3x faster without switching tools.",
                f"As an **admin**, I want to configure and control {idea} per team, so that I can enforce org-wide policies.",
                f"As a **new user**, I want {idea} to have sensible defaults, so that I can get value immediately without reading docs.",
                f"As a **developer**, I want {idea} to expose a public API, so that I can build integrations and automations.",
            ],
            "acceptance_criteria": [
                f"**AC-1**: {idea} is accessible from the main navigation within 1 click.",
                "**AC-2**: All state changes are persisted and survive page refresh.",
                "**AC-3**: Feature is behind a feature flag, rollout-able per org.",
                "**AC-4**: Unit test coverage ≥ 85%, E2E tests cover happy path + top 3 edge cases.",
                "**AC-5**: Performance: <200ms p95 for read, <500ms p95 for write operations.",
            ],
        },
        "tech_design": {
            "hld": f"# Technical Design: {idea}\n\n## Architecture Decision\nWe'll implement this as a new service module within the existing monolith, with a clear interface boundary for future extraction into a microservice.\n\n## Data Model\n- New table `features` with columns: id (UUID), org_id, config (JSONB), created_at, updated_at\n- Index on (org_id, created_at) for listing queries\n- Soft delete via `deleted_at` column",
            "modules": [
                {"name": "API Layer", "description": "REST endpoints: GET/POST/PUT/DELETE /api/v1/features. Input validation via JSON Schema. Rate limited at 100 req/min/org."},
                {"name": "Service Layer", "description": "Business logic: feature flag evaluation, permission checks, audit logging. Stateless, horizontally scalable."},
                {"name": "Data Layer", "description": "PostgreSQL with JSONB for flexible config. Read replica for list queries. Redis cache (TTL 60s) for hot paths."},
                {"name": "Event System", "description": "Publish feature.created/updated/deleted events to message bus. Consumers: audit log, analytics, webhook delivery."},
            ],
            "risks": [
                {"risk": "Schema migration on large table", "severity": "high", "mitigation": "Use online DDL (pg_repack). Run migration during low-traffic window. Rollback script prepared."},
                {"risk": "Cache invalidation complexity", "severity": "medium", "mitigation": "Event-driven invalidation. Fallback to DB on cache miss. Monitor hit rate."},
                {"risk": "Feature flag interaction bugs", "severity": "medium", "mitigation": "Integration test matrix covering flag combinations. Gradual rollout: 1% → 10% → 50% → 100%."},
            ],
        },
        "code_implementation": {
            "pr_title": f"feat: implement {idea}",
            "branch": f"feat/{idea.lower().replace(' ', '-')[:30]}",
            "files_changed": 12,
            "insertions": 847,
            "deletions": 23,
            "diff_summary": f"### Changes\n- **api/routes/features.py** — New CRUD endpoints with input validation\n- **services/feature_service.py** — Business logic, permission checks, event publishing\n- **models/feature.py** — SQLAlchemy model with JSONB config column\n- **migrations/003_add_features.py** — Alembic migration (reversible)\n- **tests/test_features.py** — 15 test cases (unit + integration)\n- **docs/api/features.md** — OpenAPI spec update",
            "review_notes": "Ready for review. All CI checks pass. Tested locally with 10k rows — p95 latency: 45ms read, 120ms write.",
        },
        "qa_testing": {
            "test_cases": [
                {"name": "Happy path — create and retrieve", "status": "✅ passed", "description": f"Create {idea} via POST, verify 201. GET by ID returns correct data. Fields match input."},
                {"name": "Validation — missing required fields", "status": "✅ passed", "description": "POST without required fields returns 400 with descriptive error. No partial data created."},
                {"name": "Authorization — viewer cannot write", "status": "✅ passed", "description": "Viewer role gets 403 on POST/PUT/DELETE. Read operations succeed."},
                {"name": "Concurrency — parallel updates", "status": "✅ passed", "description": "10 concurrent PUT requests. No lost updates (optimistic locking). Final state consistent."},
                {"name": "Performance — load test", "status": "✅ passed", "description": "1000 req/s for 60s. p50: 12ms, p95: 45ms, p99: 120ms. Zero errors. Memory stable."},
                {"name": "Edge case — max payload size", "status": "⚠️ warning", "description": "1MB JSON config accepted. 5MB rejected with 413. Consider documenting the limit."},
            ],
            "coverage": "91%",
            "summary": "6/6 test cases passed (1 with advisory warning). No blockers. Ready for staging deployment.",
        },
        "release_notes": {
            "version": "1.4.0",
            "date": "2026-04-13",
            "highlights": [
                f"🚀 **New Feature**: {idea} — full CRUD support with real-time sync",
                "⚡ **Performance**: Read operations now <50ms p95 (was 200ms)",
                "🔒 **Security**: RBAC enforcement on all new endpoints",
                "📊 **Observability**: New Prometheus metrics for feature usage tracking",
            ],
            "breaking_changes": "None",
            "migration_notes": "Run `alembic upgrade head` before deploying. Migration is backward-compatible and reversible.",
            "contributors": ["@alice (spec + design)", "@bob (implementation)", "@carol (QA)"],
        },
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
# Track user progress
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "ran_workflow" not in st.session_state:
    st.session_state.ran_workflow = False

# ── ONBOARDING FLOW (first-time users) ──────────────────────────────────────
if not st.session_state.onboarded:
    st.markdown("# 🪄 Welcome to MagiC")
    st.markdown("### Kubernetes for AI Agents — manage any AI worker, built with any tool")

    st.markdown("")
    st.markdown("""
**Imagine you have a team of AI assistants** — one writes specs, one designs architecture,
one writes code, one runs tests, one writes release notes.

**The problem?** They're all separate scripts. No coordination. No visibility. No cost control.

**MagiC fixes this.** It's a control plane that manages your AI workers like Kubernetes manages containers:
""")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 1️⃣ Workers Register")
        st.markdown("Each AI agent registers its capabilities with MagiC. Built with any framework — LangChain, CrewAI, custom code, any language.")
    with c2:
        st.markdown("#### 2️⃣ You Submit Tasks")
        st.markdown('You say "write a PRD for dark mode" — MagiC automatically finds the best worker and dispatches the task.')
    with c3:
        st.markdown("#### 3️⃣ MagiC Orchestrates")
        st.markdown("Multi-step workflows run automatically. Parallel execution. Cost tracking. Failure recovery. All managed.")

    st.markdown("")
    st.markdown("---")
    st.markdown("")

    st.markdown("### 🚀 Try it now — describe a feature you want to build:")
    quick_idea = st.text_input("", placeholder="e.g. Add dark mode to the dashboard", key="onboard_idea", label_visibility="collapsed")

    if st.button("✨ See MagiC in action", type="primary", key="onboard_btn"):
        if not quick_idea:
            quick_idea = "Add dark mode to the dashboard"

        st.session_state.onboarded = True
        st.session_state.ran_workflow = True
        st.session_state.first_idea = quick_idea

        steps = ["📝 Writing spec...", "🏗️ Designing architecture...", "💻 Writing code...", "🧪 Running tests...", "📋 Writing release notes..."]
        step_ids = ["spec", "design", "code", "qa", "release"]
        task_types = ["spec_writing", "tech_design", "code_implementation", "qa_testing", "release_notes"]
        workers = ["SpecWriter", "TechDesign", "CodeImplement", "QA", "ReleaseNotes"]

        progress_bar = st.progress(0, text="Starting workflow...")
        status = st.empty()
        outputs = {}

        for i, (step_text, sid, tt, wname) in enumerate(zip(steps, step_ids, task_types, workers)):
            progress_bar.progress((i + 1) / len(steps), text=f"{step_text} ({wname})")
            with status.container():
                for j, s in enumerate(step_ids):
                    if j < i:
                        st.markdown(f"✅ **{s}** — done")
                    elif j == i:
                        st.markdown(f"🔄 **{s}** — running on {workers[j]}...")
                    else:
                        st.markdown(f"⏳ **{s}** — waiting")
            time.sleep(1.2 if not llm_key else 0.3)
            outputs[sid] = get_output(tt, {"idea": quick_idea})

        progress_bar.progress(1.0, text="✅ Workflow complete!")
        with status.container():
            for s in step_ids:
                st.markdown(f"✅ **{s}** — done")

        st.balloons()
        st.success(f'🎉 Done! MagiC coordinated 5 AI workers to deliver "{quick_idea}" in seconds.')

        for sid, out in outputs.items():
            with st.expander(f"📄 {sid}", expanded=(sid == "spec")):
                render_output(sid, out)

        st.markdown("---")
        st.markdown("### What just happened?")
        st.markdown(f"""
1. You typed **"{quick_idea}"**
2. MagiC created a **5-step workflow** (spec → design → code + tests → release notes)
3. Each step was **routed to the best available worker** based on capabilities
4. Steps with no dependencies ran **in parallel** (code + tests)
5. Every step's **cost was tracked** and checked against budget policies
6. The entire workflow was **traced** with a single trace ID for debugging

**This is what MagiC does** — it doesn't build AI agents, it manages them.
""")

        if st.button("🔍 Explore all features →", type="primary", key="explore_btn"):
            st.rerun()

    st.stop()  # Don't show the rest of the app until onboarded

# ── MAIN APP (after onboarding) ─────────────────────────────────────────────
st.markdown("# 🪄 MagiC — AI Worker Management")
st.caption("Don't build another AI. Manage the ones you have. • [GitHub](https://github.com/kienbui1995/magic) • [Docs](https://kienbui1995.github.io/magic/docs/)")

# Mode toggle
view_mode = st.radio("", ["🟢 Essentials", "🔵 All Features"], horizontal=True, label_visibility="collapsed",
                     help="Essentials: workflows + workers + costs. All Features: routing, policies, RBAC, knowledge, architecture.")

# Top metrics
m1, m2, m3, m4, m5 = st.columns(5)
active = sum(1 for w in MOCK_WORKERS if w["status"] == "active")
total_cost = sum(w["total_cost_today"] for w in MOCK_WORKERS)
m1.metric("Workers", f"{active}/{len(MOCK_WORKERS)}", "active")
m2.metric("Teams", len(MOCK_TEAMS))
m3.metric("Cost Today", f"${total_cost:.2f}", f"budget: ${sum(t['daily_budget'] for t in MOCK_TEAMS):.0f}")
m4.metric("Policies", len(MOCK_POLICIES), "1 active")
m5.metric("Knowledge", len(MOCK_KNOWLEDGE), "entries")

# ── Output Renderer ──────────────────────────────────────────────────────────
def render_output(step_id, out):
    """Render step output as rich markdown instead of raw JSON."""
    if "prd" in out:  # spec_writing
        st.markdown(out["prd"])
        if "user_stories" in out:
            st.markdown("### User Stories")
            for s in out["user_stories"]:
                st.markdown(f"- {s}")
        if "acceptance_criteria" in out:
            st.markdown("### Acceptance Criteria")
            for ac in out["acceptance_criteria"]:
                st.markdown(f"- {ac}")
    elif "hld" in out:  # tech_design
        st.markdown(out["hld"])
        if "modules" in out:
            st.markdown("### Modules")
            for m in out["modules"]:
                if isinstance(m, dict):
                    st.markdown(f"- **{m.get('name', '?')}** — {m.get('description', '')}")
                else:
                    st.markdown(f"- {m}")
        if "risks" in out:
            st.markdown("### Risks")
            for r in out["risks"]:
                if isinstance(r, dict):
                    sev = r.get("severity", "medium")
                    icon = "🔴" if sev == "high" else "🟡" if sev == "medium" else "🟢"
                    st.markdown(f"- {icon} **{r.get('risk', '?')}** — {r.get('mitigation', '')}")
                else:
                    st.markdown(f"- {r}")
    elif "pr_title" in out:  # code_implementation
        st.markdown(f"### {out['pr_title']}")
        if "branch" in out:
            st.code(f"git checkout {out['branch']}", language="bash")
        c1, c2, c3 = st.columns(3)
        c1.metric("Files Changed", out.get("files_changed", "?"))
        c2.metric("Insertions", f"+{out.get('insertions', '?')}")
        c3.metric("Deletions", f"-{out.get('deletions', '?')}")
        if "diff_summary" in out:
            st.markdown(out["diff_summary"])
        if "review_notes" in out:
            st.info(out["review_notes"])
    elif "test_cases" in out:  # qa_testing
        st.markdown(f"### Test Results — Coverage: {out.get('coverage', 'N/A')}")
        if "summary" in out:
            st.info(out["summary"])
        for tc in out["test_cases"]:
            if isinstance(tc, dict):
                st.markdown(f"- {tc.get('status', '?')} **{tc.get('name', '?')}** — {tc.get('description', '')}")
            else:
                st.markdown(f"- {tc}")
    elif "highlights" in out:  # release_notes
        st.markdown(f"### Release {out.get('version', '?')} — {out.get('date', '')}")
        for h in out["highlights"]:
            st.markdown(f"- {h}")
        if "breaking_changes" in out and out["breaking_changes"] != "None":
            st.warning(f"⚠️ Breaking changes: {out['breaking_changes']}")
        if "migration_notes" in out:
            st.markdown(f"**Migration:** {out['migration_notes']}")
        if "contributors" in out:
            st.markdown(f"**Contributors:** {', '.join(out['contributors'])}")
    else:
        st.json(out)

# ── Why MagiC? ───────────────────────────────────────────────────────────────
with st.expander("💡 **Why MagiC?** — See the difference", expanded=False):
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("### ❌ Without MagiC")
        st.markdown("""- Each AI agent is a **standalone script** — no coordination
- **No visibility** into what agents are doing or costing
- **Manual routing** — you decide which agent handles what
- **No cost control** — surprise bills from runaway agents
- **Framework lock-in** — stuck with one tool (CrewAI OR LangChain)
- **No failure recovery** — if an agent crashes, you restart manually""")
    with b2:
        st.markdown("### ✅ With MagiC")
        st.markdown("""- Workers **join an organization**, get tasks assigned automatically
- **Real-time monitoring** — see every task, cost, and event as it happens
- **Smart routing** — best match, cheapest, fastest, or custom strategy
- **Budget guardrails** — alerts at 80%, auto-pause at 100%
- **Any framework** — CrewAI, LangChain, custom bots, any language
- **Auto-recovery** — retry, skip, reassign on failure""")

# ── Tabs ─────────────────────────────────────────────────────────────────────
if view_mode == "🟢 Essentials":
    tab_wf, tab_workers, tab_cost = st.tabs(
        ["🔄 Workflows — run AI pipelines", "🤖 Workers — your AI team", "💰 Costs — budget tracking"])
else:
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
            steps_timing = [
                ("spec", 0, 3.2, 0.05),
                ("design", 3.2, 6.0, 0.08),
                ("code", 6.0, 7.5, 0.12),
                ("qa", 6.0, 7.2, 0.04),
                ("release", 7.5, 8.3, 0.02),
            ]
            worker_names = {"spec": "SpecWriter", "design": "TechDesign", "code": "CodeImplement", "qa": "QA", "release": "ReleaseNotes"}
        else:
            bug = st.text_input("Bug Description", placeholder="e.g. Login crashes on Safari", key="wf_bug")
            steps_def = [
                {"id": "reproduce", "task_type": "qa_testing"},
                {"id": "fix", "task_type": "code_implementation", "depends_on": ["reproduce"]},
                {"id": "verify", "task_type": "qa_testing", "depends_on": ["fix"]},
            ]
            user_input = {"spec": bug, "mode": "reproduce"}
            steps_timing = [
                ("reproduce", 0, 2.0, 0.04),
                ("fix", 2.0, 4.0, 0.12),
                ("verify", 4.0, 5.0, 0.04),
            ]
            worker_names = {"reproduce": "QA", "fix": "CodeImplement", "verify": "QA"}

        failure_mode = st.selectbox("Failure simulation", ["None", "Retry (step fails then succeeds)", "Skip (step fails, workflow continues)", "Abort (step fails, workflow stops)"], key="fail_mode")

        if st.button("🚀 Launch Workflow", type="primary"):
            wf_id = f"wf_{random.randint(1000,9999)}"
            events = [f"[00.0s] workflow.started    id={wf_id}  name=\"{wf_type}\""]
            progress = st.empty()
            outputs = {}
            fail_step_idx = 2  # 3rd step (0-indexed)
            aborted = False

            for i, step in enumerate(steps_def):
                if aborted:
                    break
                sname = step["id"]
                wname = worker_names.get(sname, "Worker")
                t_start = steps_timing[i][1] if i < len(steps_timing) else 0
                t_end = steps_timing[i][2] if i < len(steps_timing) else 0
                t_cost = steps_timing[i][3] if i < len(steps_timing) else 0
                trace = f"trace_{random.randint(1000,9999)}"

                events.append(f"[{t_start:05.1f}s] task.routed         step={sname}  worker={wname}  strategy=best_match")
                events.append(f"[{t_start:05.1f}s] task.dispatched     step={sname}  worker={wname}  trace_id={trace}")

                # Show progress
                with progress.container():
                    cols = st.columns(len(steps_def))
                    for j, s in enumerate(steps_def):
                        if j < i:
                            emoji = "✅"
                        elif j == i:
                            emoji = "🔄"
                        elif aborted:
                            emoji = "🚫"
                        else:
                            emoji = "⏳"
                        cols[j].markdown(f"**{emoji} {s['id']}**")

                time.sleep(1.0 if not llm_key else 0.3)

                # Failure handling on 3rd step
                if failure_mode != "None" and i == fail_step_idx:
                    latency = int((t_end - t_start) * 1000)
                    events.append(f"[{t_end:05.1f}s] task.failed         step={sname}  error=\"simulated failure\"  latency={latency}ms")

                    if "Retry" in failure_mode:
                        with progress.container():
                            cols = st.columns(len(steps_def))
                            for j, s in enumerate(steps_def):
                                emoji = "✅" if j < i else ("❌" if j == i else "⏳")
                                cols[j].markdown(f"**{emoji} {s['id']}**")
                        time.sleep(0.5)
                        events.append(f"[{t_end:05.1f}s] task.retrying       step={sname}  attempt=2")
                        with progress.container():
                            cols = st.columns(len(steps_def))
                            for j, s in enumerate(steps_def):
                                emoji = "✅" if j < i else ("🔄" if j == i else "⏳")
                                cols[j].markdown(f"**{emoji} {s['id']}**")
                        time.sleep(1.0)
                        events.append(f"[{t_end:05.1f}s] task.completed      step={sname}  cost=${t_cost:.2f}  latency={latency}ms  (retry succeeded)")
                        outputs[sname] = get_output(step["task_type"], user_input)

                    elif "Skip" in failure_mode:
                        with progress.container():
                            cols = st.columns(len(steps_def))
                            for j, s in enumerate(steps_def):
                                emoji = "✅" if j < i else ("⏭️" if j == i else "⏳")
                                cols[j].markdown(f"**{emoji} {s['id']}**")
                        events.append(f"[{t_end:05.1f}s] task.skipped        step={sname}  on_failure=skip")
                        outputs[sname] = {"status": "skipped", "reason": "on_failure: skip"}

                    elif "Abort" in failure_mode:
                        events.append(f"[{t_end:05.1f}s] workflow.aborted    id={wf_id}  failed_step={sname}")
                        with progress.container():
                            cols = st.columns(len(steps_def))
                            for j, s in enumerate(steps_def):
                                if j < i:
                                    emoji = "✅"
                                elif j == i:
                                    emoji = "❌"
                                else:
                                    emoji = "🚫"
                                cols[j].markdown(f"**{emoji} {s['id']}**")
                        aborted = True
                        continue
                else:
                    latency = int((t_end - t_start) * 1000)
                    events.append(f"[{t_end:05.1f}s] task.completed      step={sname}  cost=${t_cost:.2f}  latency={latency}ms")
                    events.append(f"[{t_end:05.1f}s] cost.recorded       worker={wname}  total=${t_cost:.2f}  budget_pct={random.randint(1,5)}%")
                    if i + 1 < len(steps_def):
                        events.append(f"[{t_end:05.1f}s] policy.checked      step={steps_def[i+1]['id']}  ✅ allowed  0 violations")
                    outputs[sname] = get_output(step["task_type"], user_input)

            if aborted:
                st.error(f"Workflow aborted at step '{steps_def[fail_step_idx]['id']}' — on_failure: abort")
            else:
                with progress.container():
                    cols = st.columns(len(steps_def))
                    for j, s in enumerate(steps_def):
                        cols[j].markdown(f"**✅ {s['id']}**")

                total_time = steps_timing[-1][2]
                events.append(f"[{total_time:05.1f}s] workflow.completed  id={wf_id}  steps={len(steps_def)}  cost=${sum(c for _,_,_,c in steps_timing):.2f}  duration={total_time}s")
                st.success(f"Workflow completed — {len(steps_def)} steps, trace_id: `{trace}`")

                # Timeline
                st.markdown("### ⏱️ Execution Timeline")
                for name, start, end, cost in steps_timing:
                    duration = end - start
                    bar_start = int(start / total_time * 20)
                    bar_len = max(1, int(duration / total_time * 20))
                    bar = "░" * bar_start + "█" * bar_len + "░" * (20 - bar_start - bar_len)
                    st.text(f"  {name:10s} {bar}  {duration:.1f}s  ${cost:.2f}")
                st.text(f"  {'':10s} {'─' * 20}")
                total_cost = sum(c for _,_,_,c in steps_timing)
                sequential_time = sum(e - s for _,s,e,_ in steps_timing)
                st.success(f"Total: {total_time:.1f}s  ${total_cost:.2f}  (saved {sequential_time - total_time:.1f}s via parallel execution)")

            # Event stream
            with st.expander("📡 Event Stream", expanded=False):
                for evt in events:
                    st.text(evt)

            # Outputs
            for sid, out in outputs.items():
                with st.expander(f"📄 Output: {sid}", expanded=(sid == list(outputs.keys())[0] if outputs else False)):
                    render_output(sid, out)

# ── Tab 2: Workers ───────────────────────────────────────────────────────────
with tab_workers:
    st.subheader("Worker Fleet")
    st.caption("Workers register capabilities, MagiC routes tasks to the best match.")
    st.info("🎯 **Any Framework, One Control Plane** — MagiC manages workers built with LangChain, CrewAI, Go, TypeScript, or any custom tool. They all speak the same protocol.")

    for w in MOCK_WORKERS:
        status_color = "🟢" if w["status"] == "active" else "🟡" if w["status"] == "paused" else "🔴"
        cap_names = ", ".join(c["name"] for c in w["capabilities"])
        cost_pct = (w["total_cost_today"] / w["limits"]["max_cost_per_day"] * 100) if w["limits"]["max_cost_per_day"] > 0 else 0
        framework = w.get("framework", "")

        with st.expander(f"{status_color} **{w['name']}** ({framework}) — `{cap_names}`", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.metric("Status", w["status"])
            c2.metric("Cost Today", f"${w['total_cost_today']:.2f}", f"{cost_pct:.0f}% of budget")
            c3.metric("Session Mode", w.get("session_mode", "stateless"))
            st.json({"id": w["id"], "team": w["team_id"], "tags": w.get("tags", {}),
                      "capabilities": w["capabilities"], "limits": w["limits"]})

# ── Tab 3: Routing ───────────────────────────────────────────────────────────
if view_mode != "🟢 Essentials":
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
if view_mode != "🟢 Essentials":
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
if view_mode != "🟢 Essentials":
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
if view_mode != "🟢 Essentials":
 with tab_arch:
    st.subheader("MagiC Architecture")

    st.subheader("Multi-Language SDKs")
    st.caption("Same 10 lines of code in any language. Workers speak the MagiC protocol.")
    sk1, sk2, sk3 = st.columns(3)
    with sk1:
        st.markdown("**🐍 Python**")
        st.code('''from magic_ai_sdk import Worker

worker = Worker(name="MyBot",
                endpoint="http://localhost:9000")

@worker.capability("summarize",
                   description="Summarizes text")
def summarize(text: str) -> str:
    return llm.complete(text)

worker.register("http://localhost:8080")
worker.serve()''', language="python")
    with sk2:
        st.markdown("**🔵 Go**")
        st.code('''w := magic.NewWorker("MyBot",
    "http://localhost:9000")

w.Capability("summarize",
    "Summarizes text",
    func(input map[string]any) (any, error) {
        return llm.Complete(input["text"]), nil
    })

w.Register("http://localhost:8080")
w.Run()''', language="go")
    with sk3:
        st.markdown("**📘 TypeScript**")
        st.code('''import { Worker } from "magic-ai-sdk";

const worker = new Worker({
    name: "MyBot",
    endpoint: "http://localhost:9000"
});

worker.capability("summarize",
    "Summarizes text",
    async (input) => llm.complete(input.text));

await worker.register("http://localhost:8080");
worker.serve();''', language="typescript")

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

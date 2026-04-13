# 🪄 Magic Product & Engineering Assistant

[![Live Demo](https://img.shields.io/badge/Live_Demo-magic--team--assistant-FF4B4B?logo=streamlit&logoColor=white)](https://magic-team-assistant.streamlit.app)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **[👉 Try the live demo](https://magic-team-assistant.streamlit.app)** — no setup required

AI-powered assistant for PM + dev teams. Uses [MagiC](https://github.com/kienbui1995/magic) as the orchestration control plane.

<!-- screenshot -->

## Try it now

### 1. Streamlit Cloud (easiest)

Fork this repo, then deploy at [streamlit.io/cloud](https://streamlit.io/cloud).

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/kienbui1995/magic-product-eng-assistant/main/app.py)

### 2. Railway (1-click)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/magic-product-assistant)

### 3. Render (1-click)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### 4. Docker

```bash
# Easiest: all-in-one (server + workers + UI in one container)
docker compose up
# Then open http://localhost:8501

# Or split mode (separate containers):
docker compose --profile split up
```

### 5. Local

```bash
pip install -r requirements.txt
streamlit run app.py
# open http://localhost:8501
```

## What it does

```
  Streamlit UI / Slack Bot
          |
     MagiC Server (localhost:8080)
          |
  ┌───────┼───────────────────┐
  v       v       v       v   v
Spec   Design   Code    QA  Release
Writer         Impl        Notes
(:9001) (:9002) (:9003) (:9004) (:9005)
```

Submit a feature idea or bug report through the web UI. MagiC orchestrates a multi-step workflow across specialized AI workers and streams progress back in real time.

## Workers

| Worker | Port | Capability | Description |
|--------|------|------------|-------------|
| SpecWriter | 9001 | `spec_writing` | PRD drafts, user stories, acceptance criteria |
| TechDesign | 9002 | `tech_design` | HLD, module decomposition, risks |
| CodeImplement | 9003 | `code_implementation` | Code suggestions, PR diffs |
| QA | 9004 | `qa_testing` | Test cases, checklists |
| ReleaseNotes | 9005 | `release_notes` | Release notes from changelogs |

## Workflows

**Feature Delivery** — spec → design → [code, qa] → release notes

```
spec → design → code ──┐
              → qa  ───┤→ release
```

**Bug Lifecycle** — reproduce → fix → verify

```
reproduce → fix → verify
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MAGIC_SERVER_URL` | `http://localhost:8080` | MagiC server URL (set in sidebar or env) |

## Development

```bash
# 1. Start MagiC server
cd /path/to/magic && ./bin/magic serve

# 2. Start workers
pip install magic-ai-sdk
python workers/spec_writer.py &
python workers/tech_design.py &
python workers/code_implement.py &
python workers/qa.py &
python workers/release_notes.py &

# 3. Run the UI
pip install -r requirements.txt
streamlit run app.py
```

## License

Apache 2.0

# Magic Product & Engineering Assistant

AI-powered assistant for PM + dev teams. Uses [MagiC](https://github.com/kienbui1995/magic) as the orchestration control plane.

## Architecture

```
  PM / Dev
     |
  Slack Bot ──> MagiC Server (localhost:8080)
                   |
        ┌──────────┼──────────────────┐
        v          v          v       v          v
  SpecWriter  TechDesign  CodeImpl   QA    ReleaseNotes
   (:9001)    (:9002)     (:9003)  (:9004)  (:9005)
```

## Workers

| Worker | Port | Capability | Description |
|--------|------|------------|-------------|
| SpecWriter | 9001 | `spec_writing` | PRD drafts, user stories, acceptance criteria |
| TechDesign | 9002 | `tech_design` | HLD, module decomposition, risks |
| CodeImplement | 9003 | `code_implementation` | Code suggestions, PR diffs |
| QA | 9004 | `qa_testing` | Test cases, checklists |
| ReleaseNotes | 9005 | `release_notes` | Release notes from changelogs |

## Workflows

- **feature_delivery** — End-to-end: research → spec → design → [code, qa] → release notes
- **bug_lifecycle** — Reproduce → fix → verify

## Quick Start

```bash
# 1. Start MagiC server (from magic-claw repo)
cd /home/kienbm/magic-claw && ./bin/magic serve

# 2. Start all workers
pip install magic-ai-sdk
python workers/spec_writer.py &
python workers/tech_design.py &
python workers/code_implement.py &
python workers/qa.py &
python workers/release_notes.py &

# 3. Submit a feature delivery workflow
curl -X POST http://localhost:8080/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d @workflows/feature_delivery.json
```

Or with Docker Compose:

```bash
docker-compose up
```

## Slack Integration

```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_SIGNING_SECRET=...
python adapters/slack_bot.py
```

Use `/magic feature-launch <idea>` in Slack to kick off a feature delivery workflow.

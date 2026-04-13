# How to Ship a Feature

## Prerequisites

1. MagiC server running at `http://localhost:8080`
2. All workers started (see README)
3. `pip install magic-ai-sdk httpx`

## Step 1: Submit a Feature Delivery Workflow

```bash
curl -X POST http://localhost:8080/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Feature: Dark Mode",
    "steps": [
      {"id": "spec", "task_type": "spec_writing", "input": {"idea": "Add dark mode to the app", "context": "Users requested it"}},
      {"id": "design", "task_type": "tech_design", "depends_on": ["spec"], "input": {"prd": ""}},
      {"id": "code", "task_type": "code_implementation", "depends_on": ["design"], "input": {"design": ""}},
      {"id": "qa", "task_type": "qa_testing", "depends_on": ["design"], "input": {"spec": ""}},
      {"id": "release", "task_type": "release_notes", "depends_on": ["code", "qa"], "input": {"changelog": ""}}
    ]
  }'
```

## Step 2: Track Progress

```bash
# Get workflow status (use the workflow ID from step 1)
curl http://localhost:8080/api/v1/workflows/{workflow_id}
```

Each step transitions: `pending` → `running` → `completed` (or `failed`).

## Step 3: Review Outputs

Each completed step produces output accessible via the workflow status response. Key outputs:

- **spec** → PRD draft, user stories, acceptance criteria
- **design** → HLD, module list, risks
- **code** → Code suggestions, PR diff
- **qa** → Test cases, checklist
- **release** → Release notes

## Via Slack

```
/magic feature-launch Add dark mode to the app
```

The bot submits the workflow and returns a tracking link.

## Via Docker Compose

```bash
docker-compose up -d
# All workers auto-register with the MagiC server
curl -X POST http://localhost:8080/api/v1/workflows -d @workflows/feature_delivery.json
```

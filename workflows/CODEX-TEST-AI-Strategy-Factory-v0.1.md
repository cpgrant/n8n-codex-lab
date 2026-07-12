# CODEX TEST — AI Strategy Factory v0.1

## Safety status

- Exported workflow only uses synthetic input.
- It contains no credentials.
- It is exported and imported with `active: false`.
- It is not available through MCP.
- Do not activate or publish it without explicit approval.

## Purpose

The workflow provides the first n8n vertical slice for AI Strategy Factory:

1. Accept a structured strategy brief through an n8n test form.
2. Normalize multiline fields into the v0.1 API contract.
3. Call the Mac-local agent service from Docker.
4. Display the structured JSON draft for human review.
5. Record an explicit approval or rejection.
6. Generate an approved Markdown artifact only after approval.

## Runtime prerequisites

Start Docker Desktop, n8n, and the Mac-local agent service. From n8n, the agent
service URL is:

```text
http://host.docker.internal:8000
```

## Manual test

Open `CODEX TEST — AI Strategy Factory v0.1` in the n8n editor, select the
Strategy Brief Form node, choose the test/execute action, and open its test form
URL. Keep the workflow inactive and unpublished. Enter only fictional data, or
adapt the checked-in synthetic example brief.

The required fields contain synthetic defaults so the initial test can be
submitted immediately before n8n's temporary test listener expires.

The `/form-test/...` URL is tied to the current manual test execution. If the
listener expires while the form is being completed, n8n displays a submission
error. Start a new test execution and use its newly opened form. This behavior
does not indicate a FastAPI or SQLite failure.

Review the complete structured JSON on the second form page. Select `approved`
or `rejected`, enter a synthetic reviewer label, and include a comment when
rejecting.

Approval ends with an artifact filename and run ID. Rejection confirms that no
artifact was created.

## Limitations

- The form has no authentication and is for local manual testing only.
- The deterministic fake provider remains the only implemented provider.
- Production form URLs are unavailable until publication; publication is out of
  scope and requires explicit approval.
- Generated artifacts remain local and ignored by Git.
- File-based JSON or YAML brief ingestion is not implemented in v0.1.

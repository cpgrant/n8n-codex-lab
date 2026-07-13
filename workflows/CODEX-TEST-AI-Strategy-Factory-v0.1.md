# CODEX TEST — AI Strategy Factory v0.1

## Safety status

- Exported workflow only uses synthetic input.
- It contains no credentials.
- It is exported and imported with `active: false`.
- It is not available through MCP.
- Do not activate or publish it without explicit approval.

## Purpose

The workflow provides the first n8n vertical slice for AI Strategy Factory:

1. Choose a checked-in synthetic example, blank manual form, or JSON upload.
2. Validate and normalize the selected input into the v0.1 API contract.
3. Call the Mac-local agent service from Docker.
4. Generate an immutable advisory quality report for the draft.
5. Display the quality findings and structured JSON for human review.
6. Record an explicit approval or rejection.
7. Generate an approved Markdown artifact only after approval.

## Runtime prerequisites

Start Docker Desktop, n8n, and the Mac-local agent service. From n8n, the agent
service URL is:

```text
http://host.docker.internal:8000
```

## Manual test

Open `CODEX TEST — AI Strategy Factory v0.1` in the n8n editor, select the
Strategy Brief Form node, choose the test/execute action, and open its test form
URL. Keep the workflow inactive and unpublished. Select one mode:

- **Load synthetic example** immediately uses the checked-in fictional brief;
- **Enter a blank manual form** opens fields with no content defaults;
- **Upload structured JSON** accepts one `.json` object up to 64 KiB.

Manual and uploaded input require explicit confirmation that the brief is
synthetic. Upload parsing rejects multiple files, wrong extensions, malformed
JSON, arrays, unknown top-level fields, and unknown organization fields. It
never uses the uploaded filename for an artifact path and forwards no binary
data to the agent service.

The `/form-test/...` URL is tied to the current manual test execution. If the
listener expires while the form is being completed, n8n displays a submission
error. Start a new test execution and use its newly opened form. This behavior
does not indicate a FastAPI or SQLite failure.

Review the advisory score, findings, questions, and complete structured JSON on
the second form page. The quality report cannot approve, reject, or rewrite the
draft. Select `approved` or `rejected`, enter a synthetic reviewer label, and
include a comment when rejecting.

Approval ends with an artifact filename and run ID. Rejection confirms that no
artifact was created.

## Limitations

- The form has no authentication and is for local manual testing only.
- Strategy generation supports deterministic fake and opt-in local Ollama
  providers. Quality mode is controlled by the FastAPI process configuration.
- Production form URLs are unavailable until publication; publication is out of
  scope and requires explicit approval.
- Generated artifacts remain local and ignored by Git.
- YAML upload is not implemented; Stage 8 intentionally starts with JSON.
- Real or confidential client briefs remain prohibited until Stage 9.
- Workflow success, error, and manual execution data persistence is disabled to
  avoid retaining uploaded files after the active test execution.

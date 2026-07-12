# Stage 5 operational verification

## Outcome

Stage 5 verifies that the AI Strategy Factory v0.1 vertical slice is safe to
operate as a local, synthetic-data lab. It does not activate or publish the n8n
workflow and does not add a model provider.

## Automated verification

Prerequisites:

- Docker Desktop and the local `n8n` container are running.
- The FastAPI agent service is running directly on the Mac.
- `curl`, `jq`, Docker, and `rg` are available.

Run from the repository root:

```bash
scripts/verify-stage5.sh
```

The script uses a unique synthetic idempotency key and verifies:

1. The exported n8n workflow remains inactive, unavailable through MCP, and
   free of credentials.
2. n8n and the agent service are reachable from their expected network paths.
3. The production form remains unpublished.
4. A synthetic brief reaches `awaiting_review` through the fake provider.
5. Repeating the create request returns the same run as an idempotent replay.
6. An explicit rejection becomes terminal and creates no artifact.
7. Repeating the rejection returns the original result as an idempotent replay.
8. The rejected run remains readable from SQLite through the API.
9. Artifact retrieval for the rejected run returns `409 ARTIFACT_NOT_READY`.

The verifier creates one durable synthetic rejected run. This is intentional
operational test data and remains ignored by Git.

## Restart-persistence check

Record the run ID printed by `scripts/verify-stage5.sh`. Stop the agent service
with `Ctrl-C`, start it again, then retrieve that same run:

```bash
scripts/agent-start.sh
```

In another terminal:

```bash
curl -fsS http://127.0.0.1:8000/v1/strategy-runs/<RUN_ID> | jq
```

Expected result: the response still reports `status: rejected`, the recorded
review is present, and `artifact` is `null`. This demonstrates persistence
across a process restart without requiring the verifier to terminate a service
it did not start.

## Manual n8n checks

The `/form-test/...` URL exists only while n8n is listening for a manual test
execution. It can expire while a person is completing a long form. This is an
n8n editor-test constraint, not an agent-service timeout or a data-loss issue.

For development, click **Execute workflow** and submit the newly opened test
form promptly. The checked-in synthetic defaults make this convenient, but
they are not a production requirement.

A stable `/form/...` URL requires publishing/activating the workflow. That is a
separate operational decision and is prohibited unless the repository owner
gives explicit approval. Stage 5 deliberately leaves the workflow unpublished.

## Stage 5 completion criteria

- The Python test suite passes.
- `scripts/verify-stage5.sh` passes with the local services running.
- One approved manual n8n execution has generated a Markdown artifact.
- Rejection and idempotency behavior have been verified with synthetic data.
- A stored run remains readable after restarting the FastAPI process.
- `git status` contains no SQLite databases, generated artifacts, secrets,
  caches, or virtual environments.
- The existing MCP sandbox workflow remains unchanged.

## Deferred work

- Publishing or activating the n8n workflow
- A stable production form URL
- `OllamaStrategyProvider` and `gemma4:31b`
- `OpenAIStrategyProvider`
- JSON or YAML file ingestion through n8n
- Authentication, authorization, and production deployment

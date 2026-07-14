#!/usr/bin/env node

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const repositoryRoot = path.resolve(__dirname, '..');
const workflow = JSON.parse(fs.readFileSync(
  path.join(repositoryRoot, 'workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json'),
  'utf8',
));
const fixture = JSON.parse(fs.readFileSync(
  path.join(repositoryRoot, 'examples/strategy-brief.synthetic.json'),
  'utf8',
));
const nodes = Object.fromEntries(workflow.nodes.map((node) => [node.name, node]));
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;

async function executeCode(name, globals) {
  const code = nodes[name].parameters.jsCode;
  const names = Object.keys(globals);
  const fn = new AsyncFunction(...names, code);
  return fn(...names.map((key) => globals[key]));
}

async function parseUpload(value, filename = 'synthetic-brief.json') {
  const buffer = Buffer.isBuffer(value) ? value : Buffer.from(value, 'utf8');
  const item = {
    json: {
      synthetic_confirmation: ['I confirm this brief contains synthetic test data only.'],
    },
    binary: {
      brief_json: {fileName: filename},
    },
  };
  return executeCode(
    'Parse JSON Brief',
    {
      $input: {first: () => item},
      helpers: {getBinaryDataBuffer: async () => buffer},
    },
  );
}

async function expectFailure(action, pattern) {
  await assert.rejects(action, pattern);
}

async function main() {
  const example = await executeCode('Load Synthetic Example', {});
  assert.deepEqual(example[0].json, fixture);

  const manual = await executeCode('Normalize Manual Brief', {
    $json: {
      title: fixture.title,
      organization_name: fixture.organization.name,
      organization_type: fixture.organization.type,
      organization_context: fixture.organization.context,
      decision_horizon: fixture.decision_horizon,
      challenge: fixture.challenge,
      desired_outcomes: fixture.desired_outcomes.join('\n'),
      constraints: fixture.constraints.join('\n'),
      available_evidence: fixture.available_evidence.join('\n'),
      stakeholders: fixture.stakeholders.join('\n'),
      requested_by: fixture.requested_by,
      synthetic_confirmation: ['I confirm this brief contains synthetic test data only.'],
    },
  });
  assert.deepEqual(manual[0].json, fixture);

  const uploaded = await parseUpload(JSON.stringify(fixture));
  assert.deepEqual(uploaded[0].json, fixture);
  assert.equal(uploaded[0].binary, undefined);

  await expectFailure(
    () => parseUpload(JSON.stringify({...fixture, unexpected: true})),
    /Unknown brief fields: unexpected/,
  );
  await expectFailure(
    () => parseUpload(Buffer.alloc(65537, 32)),
    /exceeds the 64 KiB limit/,
  );
  await expectFailure(
    () => parseUpload(JSON.stringify(fixture), 'synthetic-brief.txt'),
    /must use a \.json extension/,
  );

  assert.equal(workflow.active, false);
  assert.equal(workflow.settings.availableInMCP, false);
  assert.equal(workflow.settings.saveDataErrorExecution, 'none');
  assert.equal(workflow.settings.saveDataSuccessExecution, 'none');
  assert.equal(workflow.settings.saveManualExecutions, true);
  console.log('Stage 8 intake verification passed.');
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});

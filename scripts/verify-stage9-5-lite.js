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

function destinations(name) {
  return (workflow.connections[name]?.main ?? [])
    .flat()
    .filter(Boolean)
    .map((connection) => connection.node);
}

async function executeCode(name, globals) {
  const code = nodes[name].parameters.jsCode;
  const names = Object.keys(globals);
  const fn = new AsyncFunction(...names, code);
  return fn(...names.map((key) => globals[key]));
}

async function main() {
  assert.equal(workflow.name, 'CODEX TEST — AI Strategy Factory v0.1');
  assert.equal(workflow.active, false);
  assert.equal(workflow.settings.availableInMCP, false);
  assert.equal(workflow.settings.saveDataErrorExecution, 'none');
  assert.equal(workflow.settings.saveDataSuccessExecution, 'none');
  assert.equal(workflow.settings.saveManualExecutions, true);
  assert.equal(
    workflow.nodes.filter((node) => Object.hasOwn(node, 'credentials')).length,
    0,
  );

  for (const required of [
    'Preserve Brief for Generation',
    'Generation Readiness',
    'Quality Review Readiness',
    'Add Review Recovery Details',
  ]) {
    assert.ok(nodes[required], `Missing Stage 9.5-lite node: ${required}`);
  }

  assert.deepEqual(destinations('Load Synthetic Example'), ['Preserve Brief for Generation']);
  assert.deepEqual(destinations('Normalize Manual Brief'), ['Preserve Brief for Generation']);
  assert.deepEqual(destinations('Parse JSON Brief'), ['Preserve Brief for Generation']);
  assert.deepEqual(destinations('Preserve Brief for Generation'), ['Generation Readiness']);
  assert.deepEqual(destinations('Generation Readiness'), ['Create Strategy Draft']);
  assert.deepEqual(destinations('Create Strategy Draft'), ['Quality Review Readiness']);
  assert.deepEqual(destinations('Quality Review Readiness'), ['Generate Quality Report']);
  assert.deepEqual(destinations('Prepare Human Review'), ['Add Review Recovery Details']);
  assert.deepEqual(destinations('Add Review Recovery Details'), ['Human Review Form']);

  const preserved = await executeCode('Preserve Brief for Generation', {$json: fixture});
  assert.deepEqual(preserved, [{json: {brief: fixture}}]);

  const triggerDescription = nodes['Strategy Brief Form'].parameters.formDescription;
  const generationNode = nodes['Generation Readiness'];
  const generationHtml = generationNode.parameters.formFields.values[0].html;
  const qualityNode = nodes['Quality Review Readiness'];
  const qualityHtml = qualityNode.parameters.formFields.values[0].html;
  const reviewCode = nodes['Add Review Recovery Details'].parameters.jsCode;
  const approvedMessage = nodes['Approved Completion'].parameters.completionMessage;
  const rejectedMessage = nodes['Rejected Completion'].parameters.completionMessage;

  assert.match(triggerDescription, /each take several minutes/);
  assert.match(generationHtml, /No run ID exists until generation finishes/);
  assert.match(generationHtml, /Do not repeatedly resubmit/);
  assert.match(qualityHtml, /scripts\/strategy-run-status\.sh/);
  assert.match(qualityHtml, /do not create another run automatically/i);
  assert.match(qualityHtml, /overflow-wrap:anywhere/);
  assert.match(qualityHtml, /<wbr>/);
  assert.match(reviewCode, /artifacts\/quality-reports\//);
  assert.match(reviewCode, /scripts\/strategy-run-status\.sh/);
  assert.match(approvedMessage, /artifacts\//);
  assert.match(approvedMessage, /artifacts\/quality-reports\//);
  assert.match(approvedMessage, /overflow-wrap:anywhere/);
  assert.match(approvedMessage, /<wbr>/);
  assert.match(rejectedMessage, /No approved strategy artifact was created/);
  assert.match(rejectedMessage, /artifacts\/quality-reports\//);
  assert.match(rejectedMessage, /overflow-wrap:anywhere/);
  assert.match(rejectedMessage, /<wbr>/);

  const create = nodes['Create Strategy Draft'].parameters;
  const quality = nodes['Generate Quality Report'].parameters;
  assert.match(create.body, /Preserve Brief for Generation/);
  assert.equal(create.options.timeout, 330000);
  assert.match(quality.url, /Create Strategy Draft/);
  assert.equal(quality.options.timeout, 330000);

  for (const node of workflow.nodes.filter((item) => item.type === 'n8n-nodes-base.httpRequest')) {
    assert.match(node.parameters.url, /^=?\{?\{?[' ]*http:\/\/host\.docker\.internal:8000|^http:\/\/host\.docker\.internal:8000/);
  }

  console.log('Stage 9.5-lite workflow verification passed.');
}

main().catch((error) => {
  console.error(error.stack ?? error.message);
  process.exit(1);
});

import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = (
    REPOSITORY_ROOT / "workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json"
)


def test_stage7_workflow_export_is_safe_and_routes_quality_before_review():
    workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}

    assert workflow["id"] == "CodexStrategyV01"
    assert workflow["name"].startswith("CODEX TEST")
    assert workflow["active"] is False
    assert workflow["settings"]["availableInMCP"] is False
    assert all("credentials" not in node for node in workflow["nodes"])
    assert len(nodes) == 11
    assert workflow["connections"]["Create Strategy Draft"]["main"][0][0][
        "node"
    ] == "Generate Quality Report"
    assert workflow["connections"]["Generate Quality Report"]["main"][0][0][
        "node"
    ] == "Prepare Human Review"

    quality_url = nodes["Generate Quality Report"]["parameters"]["url"]
    assert quality_url.endswith("+ '/quality-report' }}")
    prepare_code = nodes["Prepare Human Review"]["parameters"]["jsCode"]
    assert "report.overall_score" in prepare_code
    assert "report.checks" in prepare_code
    assert "report.issues" in prepare_code
    assert "cannot approve, reject, or rewrite" in prepare_code
    assert "escapeHtml" in prepare_code

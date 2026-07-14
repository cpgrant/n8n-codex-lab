import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = (
    REPOSITORY_ROOT / "workflows/CODEX-TEST-AI-Strategy-Factory-v0.1.json"
)


def test_stage8_workflow_export_is_safe_and_routes_quality_before_review():
    workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}

    assert workflow["id"] == "CodexStrategyV01"
    assert workflow["name"].startswith("CODEX TEST")
    assert workflow["active"] is False
    assert workflow["settings"]["availableInMCP"] is False
    assert all("credentials" not in node for node in workflow["nodes"])
    assert len(nodes) == 16
    assert workflow["settings"]["saveDataErrorExecution"] == "none"
    assert workflow["settings"]["saveDataSuccessExecution"] == "none"
    assert workflow["settings"]["saveManualExecutions"] is False
    assert workflow["connections"]["Strategy Brief Form"]["main"][0][0][
        "node"
    ] == "Choose Input Mode"
    intake_outputs = workflow["connections"]["Choose Input Mode"]["main"]
    assert [output[0]["node"] for output in intake_outputs] == [
        "Load Synthetic Example",
        "Blank Manual Brief Form",
        "JSON Upload Form",
    ]
    assert workflow["connections"]["Load Synthetic Example"]["main"][0][0][
        "node"
    ] == "Create Strategy Draft"
    assert workflow["connections"]["Blank Manual Brief Form"]["main"][0][0][
        "node"
    ] == "Normalize Manual Brief"
    assert workflow["connections"]["JSON Upload Form"]["main"][0][0][
        "node"
    ] == "Parse JSON Brief"
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


def test_stage9_1_workflow_requires_human_and_service_authentication():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow = json.loads(workflow_text)
    nodes = {node["name"]: node for node in workflow["nodes"]}
    trigger = nodes["Strategy Brief Form"]

    assert trigger["typeVersion"] >= 2.6
    assert trigger["parameters"]["authentication"] == "n8nUserAuth"
    assert trigger["parameters"]["options"]["includeUserInOutput"] is True

    def headers(node_name):
        parameters = nodes[node_name]["parameters"]["headerParameters"][
            "parameters"
        ]
        return {item["name"]: item["value"] for item in parameters}

    create_headers = headers("Create Strategy Draft")
    quality_headers = headers("Generate Quality Report")
    review_headers = headers("Record Review Decision")
    assert create_headers["Authorization"] == (
        "={{ 'Bearer ' + $env.AI_FACTORY_SERVICE_TOKEN }}"
    )
    assert quality_headers["Authorization"] == (
        "={{ 'Bearer ' + $env.AI_FACTORY_SERVICE_TOKEN }}"
    )
    assert review_headers["Authorization"] == (
        "={{ 'Bearer ' + $env.AI_FACTORY_REVIEW_TOKEN }}"
    )
    assert review_headers["X-AI-Factory-Actor-ID"] == "={{ $json.user.id }}"

    review_fields = nodes["Human Review Form"]["parameters"]["formFields"][
        "values"
    ]
    assert all(field.get("fieldName") != "reviewer" for field in review_fields)
    review_body = nodes["Record Review Decision"]["parameters"]["body"]
    assert "reviewer: $json.user.id" in review_body
    assert "AI_FACTORY_SERVICE_TOKEN=" not in workflow_text
    assert "AI_FACTORY_REVIEW_TOKEN=" not in workflow_text
    assert all("credentials" not in node for node in workflow["nodes"])


def test_stage8_intake_modes_are_blank_bounded_and_strict():
    workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}

    trigger_fields = nodes["Strategy Brief Form"]["parameters"]["formFields"][
        "values"
    ]
    assert trigger_fields[0]["fieldName"] == "input_mode"
    assert [
        item["option"]
        for item in trigger_fields[0]["fieldOptions"]["values"]
    ] == [
        "Load synthetic example",
        "Enter a blank manual form",
        "Upload structured JSON",
    ]

    manual_fields = nodes["Blank Manual Brief Form"]["parameters"][
        "formFields"
    ]["values"]
    assert all("defaultValue" not in field for field in manual_fields)
    assert any(
        field.get("fieldName") == "synthetic_confirmation"
        and field.get("requiredField") is True
        for field in manual_fields
    )

    upload_fields = nodes["JSON Upload Form"]["parameters"]["formFields"][
        "values"
    ]
    file_field = next(
        field for field in upload_fields if field.get("fieldType") == "file"
    )
    assert file_field["multipleFiles"] is False
    assert file_field["acceptFileTypes"] == ".json"
    assert file_field["requiredField"] is True

    parser = nodes["Parse JSON Brief"]["parameters"]["jsCode"]
    assert "buffer.length > 65536" in parser
    assert "binaryKeys.length !== 1" in parser
    assert "Unknown brief fields" in parser
    assert "Unknown organization fields" in parser
    assert "getBinaryDataBuffer" in parser
    assert "filename" not in parser.split("return [{ json:", 1)[1]
    assert "item.binary" not in parser.split("return [{ json:", 1)[1]

    example = nodes["Load Synthetic Example"]["parameters"]["jsCode"]
    fixture = json.loads(
        (REPOSITORY_ROOT / "examples/strategy-brief.synthetic.json").read_text(
            encoding="utf-8"
        )
    )
    assert fixture["title"] in example
    assert fixture["organization"]["name"] in example

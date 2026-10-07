from app.main import AnalyzeRequest, analyze_failure


def test_detects_security_gate():
    result = analyze_failure(AnalyzeRequest(workflow="ci", logs="Trivy found a HIGH vulnerability"))
    assert result.recommendations[0].category == "security"
    assert result.recommendations[0].confidence > 0.9


def test_unknown_logs_get_safe_recommendation():
    result = analyze_failure(AnalyzeRequest(workflow="ci", logs="unexpected runner message"))
    assert result.recommendations[0].category == "unknown"

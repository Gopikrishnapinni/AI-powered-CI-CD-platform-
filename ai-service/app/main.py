from collections.abc import Iterable
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="CI Failure Analyzer", version="1.0.0")


class AnalyzeRequest(BaseModel):
    workflow: str = Field(min_length=1, max_length=100)
    logs: str = Field(min_length=1, max_length=100_000)
    failed_step: str | None = Field(default=None, max_length=200)


class Recommendation(BaseModel):
    category: Literal["dependency", "test", "security", "deployment", "infrastructure", "unknown"]
    confidence: float
    root_cause: str
    recommendation: str
    evidence: list[str]


class AnalyzeResponse(BaseModel):
    workflow: str
    summary: str
    recommendations: list[Recommendation]


def _contains_any(text: str, values: Iterable[str]) -> bool:
    return any(value in text for value in values)


def analyze_failure(request: AnalyzeRequest) -> AnalyzeResponse:
    logs = request.logs.lower()
    recommendations: list[Recommendation] = []

    if _contains_any(logs, ("connection refused", "could not connect", "timeout")):
        recommendations.append(Recommendation(
            category="infrastructure",
            confidence=0.91,
            root_cause="A dependent service or infrastructure endpoint was unavailable.",
            recommendation="Verify service readiness, network policy, security groups, DNS, and dependency environment variables.",
            evidence=["connection refused/timeout signal found in logs"],
        ))
    if _contains_any(logs, ("compilation failure", "cannot find symbol", "maven-compiler-plugin")):
        recommendations.append(Recommendation(
            category="dependency",
            confidence=0.88,
            root_cause="The application did not compile with the configured JDK or dependency graph.",
            recommendation="Run mvn dependency:tree, verify the Java version, and check recently changed imports or dependency versions.",
            evidence=["compiler failure signal found in logs"],
        ))
    if _contains_any(logs, ("assertionerror", "test failure", "tests run:", "failed to execute goal")):
        recommendations.append(Recommendation(
            category="test",
            confidence=0.86,
            root_cause="One or more automated tests failed.",
            recommendation="Inspect the first failing test, reproduce it locally, and check for flaky time or environment assumptions.",
            evidence=["test failure signal found in logs"],
        ))
    if _contains_any(logs, ("critical", "high vulnerability", "trivy", "sonarqube quality gate")):
        recommendations.append(Recommendation(
            category="security",
            confidence=0.93,
            root_cause="A security or code-quality gate blocked the pipeline.",
            recommendation="Review the scanner report, upgrade affected dependencies/base images, and document any approved exception.",
            evidence=["security gate signal found in logs"],
        ))
    if _contains_any(logs, ("readiness probe failed", "imagepullbackoff", "helm upgrade", "rollback")):
        recommendations.append(Recommendation(
            category="deployment",
            confidence=0.9,
            root_cause="The Kubernetes release did not become healthy.",
            recommendation="Inspect pod events and logs, validate image/tag and probe paths, then use Helm history before retrying.",
            evidence=["Kubernetes/Helm failure signal found in logs"],
        ))

    if not recommendations:
        recommendations.append(Recommendation(
            category="unknown",
            confidence=0.35,
            root_cause="No known failure signature was detected.",
            recommendation="Review the first error in the job log and attach the complete failing step output for deeper analysis.",
            evidence=["no supported failure signature found"],
        ))

    return AnalyzeResponse(
        workflow=request.workflow,
        summary=f"Detected {len(recommendations)} likely cause(s) for workflow '{request.workflow}'.",
        recommendations=recommendations,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_failure(request)

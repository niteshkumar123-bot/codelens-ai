from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.models import (
    Project,
    CodeSubmission,
    AnalysisRun,
    Finding,
    TestRun,
)
from app.schemas.schemas import AnalyzeRequest, AnalysisReportResponse

from app.analyzers.syntax_analyzer import SyntaxAnalyzer
from app.analyzers.ast_visitor import ASTAnalyzer
from app.analyzers.security_analyzer import SecurityAnalyzer
from app.analyzers.quality_analyzer import QualityAnalyzer
from app.analyzers.complexity_analyzer import ComplexityAnalyzer
from app.analyzers.test_generator import TestGenerator

from app.sandbox.docker_sandbox import DockerSandbox


router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/", response_model=AnalysisReportResponse)
def run_analysis(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db)
):

    # ---------------------------------------------------------
    # 1. Save submission
    # ---------------------------------------------------------

    submission = CodeSubmission(
        project_id=payload.project_id,
        code=payload.code,
        filename=payload.filename
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    # ---------------------------------------------------------
    # 2. Create analysis run
    # ---------------------------------------------------------

    run = AnalysisRun(
        submission_id=submission.id,
        status="RUNNING"
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    # ---------------------------------------------------------
    # 3. Syntax analysis
    # ---------------------------------------------------------

    syntax_res = SyntaxAnalyzer.analyze(payload.code)

    all_findings = []

    if not syntax_res["valid"]:

        err = syntax_res["error"]

        all_findings.append({
            "category": "syntax",
            "severity": "critical",
            "confidence": 1.0,
            "rule_id": err["type"],
            "title": f'{err["type"]}: {err["message"]}',
            "description": err["message"],
            "line": err["line"],
            "column": err["column"],
            "evidence": err["evidence"],
            "recommendation": err["suggestion"]
        })

        run.syntax_valid = 0

    else:

        run.syntax_valid = 1

        # -----------------------------------------------------
        # 4. Static analysis
        # -----------------------------------------------------

        all_findings.extend(
            ASTAnalyzer.analyze(payload.code)
        )

        all_findings.extend(
            SecurityAnalyzer.analyze(payload.code)
        )

        all_findings.extend(
            QualityAnalyzer.analyze(payload.code)
        )

    # ---------------------------------------------------------
    # 5. Complexity analysis
    # ---------------------------------------------------------

    metrics = ComplexityAnalyzer.analyze(payload.code)

    # ---------------------------------------------------------
    # 6. Automated test generation + execution
    # ---------------------------------------------------------

    if syntax_res["valid"]:

        test_code = TestGenerator.generate_tests(
            payload.code
        )

        sandbox_res = DockerSandbox.execute_code(
            payload.code,
            test_code
        )

    else:

        sandbox_res = {
            "exit_code": -1,
            "output": "",
            "error": "Tests skipped because the code contains a syntax error.",
            "passed_tests": 0,
            "failed_tests": 0
        }

    # ---------------------------------------------------------
    # 7. Test results
    # ---------------------------------------------------------

    passed_tests = sandbox_res.get(
        "passed_tests",
        0
    )

    failed_tests = sandbox_res.get(
        "failed_tests",
        0
    )

    execution_output = (
        sandbox_res.get("output")
        or sandbox_res.get("error")
        or ""
    )

    # ---------------------------------------------------------
    # 8. Convert runtime/test failures into findings
    # ---------------------------------------------------------

    if syntax_res["valid"] and failed_tests > 0:

        runtime_error = sandbox_res.get(
            "error"
        )

        if not runtime_error:
            runtime_error = execution_output

        all_findings.append({
            "category": "runtime",
            "severity": "high",
            "confidence": 1.0,
            "rule_id": "RUNTIME_ERROR",
            "title": "Automated test execution failed",
            "description": runtime_error,
            "line": None,
            "column": None,
            "evidence": execution_output,
            "recommendation": (
                "Review the failing test and fix the runtime "
                "error before executing the code again."
            )
        })

    # ---------------------------------------------------------
    # 9. Save test run
    # ---------------------------------------------------------

    test_run = TestRun(
        analysis_run_id=run.id,
        total_tests=passed_tests + failed_tests,
        passed_tests=passed_tests,
        failed_tests=failed_tests,
        execution_output=execution_output
    )

    db.add(test_run)

    # ---------------------------------------------------------
    # 10. Save findings
    # ---------------------------------------------------------

    for finding in all_findings:

        db.add(
            Finding(
                analysis_run_id=run.id,
                **finding
            )
        )

    # ---------------------------------------------------------
    # 11. Calculate score
    # ---------------------------------------------------------

    score = 100.0 - (
        len(all_findings) * 5.0
    )

    score = max(
        0.0,
        min(
            100.0,
            score
        )
    )

    # ---------------------------------------------------------
    # 12. Complete analysis
    # ---------------------------------------------------------

    run.status = "COMPLETED"
    run.overall_score = score
    run.metrics = metrics

    db.commit()
    db.refresh(run)

    # ---------------------------------------------------------
    # 13. Return report
    # ---------------------------------------------------------

    return {
        "analysis_id": run.id,
        "status": run.status,
        "overall_score": run.overall_score,
        "syntax_valid": bool(run.syntax_valid),
        "metrics": run.metrics,
        "findings": all_findings,
        "test_runs": [
            {
                "total_tests": test_run.total_tests,
                "passed_tests": test_run.passed_tests,
                "failed_tests": test_run.failed_tests,
                "execution_output": test_run.execution_output
            }
        ],
        "created_at": run.created_at
    }


@router.get(
    "/{analysis_id}",
    response_model=AnalysisReportResponse
)
def get_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db)
):

    run = (
        db.query(AnalysisRun)
        .filter(
            AnalysisRun.id == analysis_id
        )
        .first()
    )

    if not run:

        raise HTTPException(
            status_code=404,
            detail="Analysis run not found"
        )

    findings = (
        db.query(Finding)
        .filter(
            Finding.analysis_run_id == run.id
        )
        .all()
    )

    test_runs = (
        db.query(TestRun)
        .filter(
            TestRun.analysis_run_id == run.id
        )
        .all()
    )

    return {
        "analysis_id": run.id,
        "status": run.status,
        "overall_score": (
            run.overall_score
            if run.overall_score is not None
            else 100.0
        ),
        "syntax_valid": bool(run.syntax_valid),
        "metrics": run.metrics or {},
        "findings": findings,
        "test_runs": test_runs,
        "created_at": run.created_at
    }


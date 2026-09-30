from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class AnalyzeRequest(BaseModel):
    project_id: UUID
    code: str
    filename: Optional[str] = "main.py"

class FindingSchema(BaseModel):
    category: str
    severity: str
    confidence: float
    rule_id: str
    title: str
    description: str
    line: Optional[int] = None
    column: Optional[int] = None
    evidence: Optional[str] = None
    recommendation: Optional[str] = None

    class Config:
        from_attributes = True

class TestRunSchema(BaseModel):
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_output: Optional[str] = None

    class Config:
        from_attributes = True

class AnalysisReportResponse(BaseModel):
    analysis_id: UUID
    status: str
    overall_score: float
    syntax_valid: bool
    metrics: Dict[str, Any]
    findings: List[FindingSchema]
    test_runs: Optional[List[TestRunSchema]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionGenerateRequest(BaseModel):
    topic: str
    difficulty: str
    concepts: List[str]
    count: int = 1

class QuestionResponse(BaseModel):
    id: UUID
    title: str
    topic: str
    difficulty: str
    problem_statement: str
    constraints: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None
    reference_solution: Optional[str] = None

    class Config:
        from_attributes = True

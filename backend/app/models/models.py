import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects")
    submissions = relationship("CodeSubmission", back_populates="project", cascade="all, delete-orphan")

class CodeSubmission(Base):
    __tablename__ = "code_submissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    code = Column(Text, nullable=False)
    filename = Column(String, default="main.py")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="submissions")
    analysis_runs = relationship("AnalysisRun", back_populates="submission", cascade="all, delete-orphan")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("code_submissions.id"), nullable=False)
    status = Column(String, default="QUEUED")
    overall_score = Column(Float, nullable=True)
    syntax_valid = Column(Integer, default=1)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("CodeSubmission", back_populates="analysis_runs")
    findings = relationship("Finding", back_populates="analysis_run", cascade="all, delete-orphan")
    test_runs = relationship("TestRun", back_populates="analysis_run", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_run_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False)
    category = Column(String, nullable=False) # syntax, ast, security, quality, complexity, logic
    severity = Column(String, nullable=False) # critical, high, medium, low, info
    confidence = Column(Float, default=1.0)
    rule_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    line = Column(Integer, nullable=True)
    column = Column(Integer, nullable=True)
    evidence = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)

    analysis_run = relationship("AnalysisRun", back_populates="findings")

class TestRun(Base):
    __tablename__ = "test_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_run_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id"), nullable=False)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    execution_output = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis_run = relationship("AnalysisRun", back_populates="test_runs")

class Question(Base):
    __tablename__ = "questions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    problem_statement = Column(Text, nullable=False)
    constraints = Column(Text, nullable=True)
    examples = Column(JSON, nullable=True)
    hidden_test_cases = Column(JSON, nullable=True)
    reference_solution = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

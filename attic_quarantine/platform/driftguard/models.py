"""Database models for DriftGuard."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, JSON, Text, ForeignKey, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Organization(Base):
    """Organization model."""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    projects = relationship("Project", back_populates="organization")


class Project(Base):
    """Project model."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    prompts = relationship("Prompt", back_populates="project")


class Prompt(Base):
    """Prompt model."""
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="prompts")
    versions = relationship("PromptVersion", back_populates="prompt")


class PromptVersion(Base):
    """Prompt version model."""
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    version = Column(String(50), nullable=False)
    template = Column(Text, nullable=False)
    meta = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    prompt = relationship("Prompt", back_populates="versions")
    eval_runs = relationship("EvalRun", back_populates="prompt_version")


class Dataset(Base):
    """Dataset model."""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    test_cases = relationship("TestCase", back_populates="dataset")


class TestCase(Base):
    """Test case model."""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    input_data = Column(JSON, nullable=False)
    expected_output = Column(Text)
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    dataset = relationship("Dataset", back_populates="test_cases")
    eval_results = relationship("EvalResult", back_populates="test_case")


class EvalRun(Base):
    """Evaluation run model."""
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True)
    prompt_version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    config = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

    # Relationships
    prompt_version = relationship("PromptVersion", back_populates="eval_runs")
    results = relationship("EvalResult", back_populates="eval_run")
    alerts = relationship("Alert", back_populates="eval_run")


class EvalResult(Base):
    """Evaluation result model."""
    __tablename__ = "eval_results"

    id = Column(Integer, primary_key=True)
    eval_run_id = Column(Integer, ForeignKey("eval_runs.id"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    output = Column(Text)
    score = Column(Float)
    metrics = Column(JSON, default=dict)
    latency_ms = Column(Integer)
    cost = Column(Float)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    eval_run = relationship("EvalRun", back_populates="results")
    test_case = relationship("TestCase", back_populates="eval_results")


class Alert(Base):
    """Alert model."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    eval_run_id = Column(Integer, ForeignKey("eval_runs.id"), nullable=False)
    alert_type = Column(String(100), nullable=False)  # drift, budget, quality
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    meta = Column(JSON, default=dict)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)

    # Relationships
    eval_run = relationship("EvalRun", back_populates="alerts")

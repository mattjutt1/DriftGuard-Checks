"""DriftGuard FastAPI application."""

import os
from typing import Optional, Any, Dict
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from .database import get_db_session, create_tables
from .models import Organization, Project, Prompt, PromptVersion
from .alerts.slack import notify_slack_sync

# Check offline mode
PROMPTOPS_MODE = os.getenv("PROMPTOPS_MODE", "production")
DISABLE_NETWORK = os.getenv("DISABLE_NETWORK", "0").lower() in ("1", "true", "yes")
ALLOW_NETWORK = os.getenv("ALLOW_NETWORK", "0").lower() in ("1", "true", "yes")

if PROMPTOPS_MODE != "stub" and DISABLE_NETWORK and not ALLOW_NETWORK:
    raise RuntimeError("PROMPTOPS_MODE is not 'stub' but network is disabled. Set ALLOW_NETWORK=1 to override.")

app = FastAPI(
    title="DriftGuard",
    description="Prompt registry and drift monitoring platform",
    version="0.1.0",
)


@app.on_event("startup")
async def startup():
    """Create tables on startup."""
    await create_tables()


class PromptRegistration(BaseModel):
    """Schema for registering a new prompt."""
    name: str = Field(..., description="Unique prompt name")
    version: str = Field(..., description="Semantic version")
    template: str = Field(..., description="Prompt template with {variables}")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DriftCheck(BaseModel):
    """Schema for drift check results."""
    prompt_id: str
    version: str
    drift_score: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    details: Dict[str, Any] = Field(default_factory=dict)


class Budget(BaseModel):
    """Schema for cost/latency budgets."""
    prompt_id: str
    max_cost_per_1k: float = Field(..., gt=0.0, description="Max cost per 1k tokens")
    max_latency_ms: int = Field(..., gt=0, description="Max latency in milliseconds")
    alert_threshold: float = Field(default=0.9, ge=0.0, le=1.0)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DriftGuard",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/v1/prompts", status_code=201)
async def register_prompt(prompt: PromptRegistration, db: AsyncSession = Depends(get_db_session)):
    """Register a new prompt in the registry."""
    # Create default org and project for now (simplified)
    org_result = await db.execute(select(Organization).where(Organization.slug == "default"))
    org = org_result.scalar_one_or_none()
    if not org:
        org = Organization(name="Default Organization", slug="default")
        db.add(org)
        await db.flush()

    project_result = await db.execute(
        select(Project).where(Project.slug == "default", Project.organization_id == org.id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        project = Project(
            organization_id=org.id,
            name="Default Project",
            slug="default"
        )
        db.add(project)
        await db.flush()

    # Create or get prompt
    prompt_result = await db.execute(
        select(Prompt).where(Prompt.name == prompt.name, Prompt.project_id == project.id)
    )
    db_prompt = prompt_result.scalar_one_or_none()
    if not db_prompt:
        db_prompt = Prompt(project_id=project.id, name=prompt.name)
        db.add(db_prompt)
        await db.flush()

    # Check if version exists
    version_result = await db.execute(
        select(PromptVersion).where(
            PromptVersion.prompt_id == db_prompt.id,
            PromptVersion.version == prompt.version
        )
    )
    if version_result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Prompt version already exists")

    # Create new version
    prompt_version = PromptVersion(
        prompt_id=db_prompt.id,
        version=prompt.version,
        template=prompt.template,
        meta=prompt.metadata,
    )
    db.add(prompt_version)
    await db.flush()

    return {"id": prompt_version.id, "status": "registered"}


@app.get("/api/v1/prompts")
async def list_prompts(
    name: Optional[str] = Query(None, description="Filter by prompt name"),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session)
):
    """List registered prompts."""
    query = select(PromptVersion).join(Prompt)
    if name:
        query = query.where(Prompt.name == name)
    query = query.limit(limit)

    result = await db.execute(query)
    versions = result.scalars().all()

    prompts = []
    for version in versions:
        prompts.append({
            "id": version.id,
            "name": version.prompt.name,
            "version": version.version,
            "template": version.template,
            "metadata": version.meta,
            "created_at": version.created_at.isoformat(),
        })

    return {"prompts": prompts, "total": len(prompts)}


@app.get("/api/v1/prompts/{prompt_id}")
async def get_prompt(prompt_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get details of a specific prompt version."""
    result = await db.execute(select(PromptVersion).where(PromptVersion.id == prompt_id))
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return {
        "id": version.id,
        "name": version.prompt.name,
        "version": version.version,
        "template": version.template,
        "metadata": version.meta,
        "created_at": version.created_at.isoformat(),
    }


@app.post("/api/v1/drift/check")
async def check_drift(check: DriftCheck):
    """Submit a drift check result (stub for now)."""
    # Mock analysis - would be implemented with database
    alert_triggered = check.drift_score > 0.3

    return {
        "status": "recorded",
        "alert_triggered": alert_triggered,
        "drift_score": check.drift_score,
    }


@app.get("/api/v1/drift/history")
async def get_drift_history(
    prompt_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """Get drift check history (stub for now)."""
    return {"checks": [], "total": 0}


@app.post("/api/v1/budgets")
async def set_budget(budget: Budget):
    """Set cost/latency budget for a prompt (stub for now)."""
    return {"status": "budget_set", "prompt_id": budget.prompt_id}


@app.get("/api/v1/budgets/{prompt_id}")
async def get_budget(prompt_id: str):
    """Get budget configuration for a prompt (stub for now)."""
    raise HTTPException(status_code=404, detail="Budget not found")


@app.get("/api/v1/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db_session)):
    """Get platform metrics."""
    org_count = await db.execute(select(Organization))
    prompt_count = await db.execute(select(Prompt))

    return {
        "total_prompts": len(prompt_count.scalars().all()),
        "total_organizations": len(org_count.scalars().all()),
        "timestamp": datetime.utcnow().isoformat(),
    }


# Alert endpoints
class AlertTest(BaseModel):
    """Schema for testing alerts."""
    message: str = Field(..., description="Alert message")
    severity: str = Field(default="info", description="Alert severity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional data")


@app.post("/api/v1/alerts/test")
async def test_alert(alert: AlertTest):
    """Test alert endpoint for Slack notifications."""
    message_payload = {
        "text": f"[{alert.severity.upper()}] {alert.message}",
        "metadata": alert.metadata,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Use sync wrapper since this is a sync endpoint
    result = notify_slack_sync(message_payload)

    return {
        "alert_sent": True,
        "action_taken": result.get("action", "unknown"),
        "status": result.get("status", "unknown"),
        "network_allowed": result.get("network_allowed", False),
        "webhook_configured": result.get("webhook_configured", False),
        "result": result
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""DriftGuard FastAPI application."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import uuid

app = FastAPI(
    title="DriftGuard",
    description="Prompt registry and drift monitoring platform",
    version="0.1.0",
)

# In-memory store
prompt_registry: Dict[str, Dict] = {}
drift_checks: List[Dict] = []
budgets: Dict[str, Dict] = {}


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
async def register_prompt(prompt: PromptRegistration):
    """Register a new prompt in the registry."""
    prompt_id = f"{prompt.name}:{prompt.version}"

    if prompt_id in prompt_registry:
        raise HTTPException(status_code=409, detail="Prompt version already exists")

    prompt_registry[prompt_id] = {
        "id": str(uuid.uuid4()),
        "name": prompt.name,
        "version": prompt.version,
        "template": prompt.template,
        "metadata": prompt.metadata,
        "created_at": datetime.utcnow().isoformat(),
        "drift_checks": [],
    }

    return {"id": prompt_registry[prompt_id]["id"], "status": "registered"}


@app.get("/api/v1/prompts")
async def list_prompts(
    name: Optional[str] = Query(None, description="Filter by prompt name"),
    limit: int = Query(100, ge=1, le=1000),
):
    """List registered prompts."""
    results = []
    for prompt_id, prompt_data in prompt_registry.items():
        if name and prompt_data["name"] != name:
            continue
        results.append(prompt_data)
        if len(results) >= limit:
            break

    return {"prompts": results, "total": len(results)}


@app.get("/api/v1/prompts/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Get details of a specific prompt."""
    if prompt_id not in prompt_registry:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return prompt_registry[prompt_id]


@app.post("/api/v1/drift/check")
async def check_drift(check: DriftCheck):
    """Submit a drift check result."""
    drift_checks.append(check.model_dump())

    # Update prompt registry with latest drift check
    prompt_key = f"{check.prompt_id}:{check.version}"
    if prompt_key in prompt_registry:
        prompt_registry[prompt_key]["drift_checks"].append({
            "drift_score": check.drift_score,
            "timestamp": check.timestamp.isoformat(),
        })

    # Mock analysis - in production, this would trigger alerts
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
    """Get drift check history."""
    results = drift_checks
    if prompt_id:
        results = [d for d in results if d["prompt_id"] == prompt_id]

    return {"checks": results[:limit], "total": len(results)}


@app.post("/api/v1/budgets")
async def set_budget(budget: Budget):
    """Set cost/latency budget for a prompt."""
    budget_key = budget.prompt_id
    budgets[budget_key] = budget.model_dump()

    return {"status": "budget_set", "prompt_id": budget.prompt_id}


@app.get("/api/v1/budgets/{prompt_id}")
async def get_budget(prompt_id: str):
    """Get budget configuration for a prompt."""
    if prompt_id not in budgets:
        raise HTTPException(status_code=404, detail="Budget not found")

    return budgets[prompt_id]


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get platform metrics."""
    return {
        "total_prompts": len(prompt_registry),
        "total_drift_checks": len(drift_checks),
        "active_budgets": len(budgets),
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

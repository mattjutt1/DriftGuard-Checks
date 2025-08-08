"""Budget manager for tracking and enforcing cost limits."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os


@dataclass
class BudgetLimit:
    """Budget limit configuration."""
    org_slug: str
    project_slug: str
    monthly_limit_usd: float
    alert_threshold: float = 0.8  # Alert when 80% of budget used
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SpendRecord:
    """Individual spending record."""
    org_slug: str
    project_slug: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class BudgetManager:
    """Manages budget limits and spending tracking."""

    def __init__(self, db_path: str = None, pricing_file: str = None):
        """
        Initialize budget manager.

        Args:
            db_path: Path to SQLite database file
            pricing_file: Path to pricing JSON file
        """
        self.db_path = db_path or self._get_default_db_path()
        self.pricing_file = pricing_file or self._get_default_pricing_file()
        self._init_database()
        self._load_pricing()

    def _get_default_db_path(self) -> str:
        """Get default database path."""
        # Use XDG_DATA_HOME or fallback to ~/.local/share
        data_dir = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        promptops_dir = Path(data_dir) / "promptops"
        promptops_dir.mkdir(parents=True, exist_ok=True)
        return str(promptops_dir / "budget.db")

    def _get_default_pricing_file(self) -> str:
        """Get default pricing file path."""
        # Use pricing file in the library directory
        lib_dir = Path(__file__).parent
        return str(lib_dir / "provider_pricing.json")

    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budget_limits (
                    org_slug TEXT,
                    project_slug TEXT,
                    monthly_limit_usd REAL,
                    alert_threshold REAL,
                    created_at TEXT,
                    updated_at TEXT,
                    PRIMARY KEY (org_slug, project_slug)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS spend_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    org_slug TEXT,
                    project_slug TEXT,
                    provider TEXT,
                    model TEXT,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost_usd REAL,
                    timestamp TEXT,
                    metadata TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_spend_org_project_month
                ON spend_records (org_slug, project_slug, timestamp)
            """)

    def _load_pricing(self):
        """Load pricing data from JSON file."""
        try:
            with open(self.pricing_file, 'r') as f:
                self.pricing = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Fall back to default pricing if file doesn't exist
            self.pricing = self._get_default_pricing()
            self._save_default_pricing()

    def _get_default_pricing(self) -> Dict[str, Any]:
        """Get default pricing structure."""
        return {
            "version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "currency": "USD",
            "providers": {
                "openai": {
                    "gpt-4o-mini": {
                        "input_cost_per_1k": 0.00015,
                        "output_cost_per_1k": 0.0006
                    },
                    "gpt-4o": {
                        "input_cost_per_1k": 0.0025,
                        "output_cost_per_1k": 0.01
                    },
                    "gpt-3.5-turbo": {
                        "input_cost_per_1k": 0.0005,
                        "output_cost_per_1k": 0.0015
                    }
                },
                "anthropic": {
                    "claude-3-5-sonnet-20241022": {
                        "input_cost_per_1k": 0.003,
                        "output_cost_per_1k": 0.015
                    },
                    "claude-3-haiku-20240307": {
                        "input_cost_per_1k": 0.00025,
                        "output_cost_per_1k": 0.00125
                    }
                }
            }
        }

    def _save_default_pricing(self):
        """Save default pricing to file."""
        try:
            os.makedirs(os.path.dirname(self.pricing_file), exist_ok=True)
            with open(self.pricing_file, 'w') as f:
                json.dump(self.pricing, f, indent=2)
        except Exception:
            # If we can't write the file, continue with in-memory pricing
            pass

    def calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for API usage.

        Args:
            provider: Provider name (e.g., "openai", "anthropic")
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD

        Raises:
            KeyError: If provider/model not found in pricing
        """
        try:
            model_pricing = self.pricing["providers"][provider][model]
            input_cost = (input_tokens / 1000) * model_pricing["input_cost_per_1k"]
            output_cost = (output_tokens / 1000) * model_pricing["output_cost_per_1k"]
            return input_cost + output_cost
        except KeyError as e:
            raise KeyError(f"Pricing not found for {provider}/{model}: {e}")

    def set_budget(self, org_slug: str, project_slug: str, monthly_limit_usd: float, alert_threshold: float = 0.8):
        """
        Set budget limit for an org/project.

        Args:
            org_slug: Organization slug
            project_slug: Project slug
            monthly_limit_usd: Monthly spending limit in USD
            alert_threshold: Fraction of budget that triggers alerts
        """
        now = datetime.utcnow().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO budget_limits
                (org_slug, project_slug, monthly_limit_usd, alert_threshold, created_at, updated_at)
                VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM budget_limits
                                           WHERE org_slug = ? AND project_slug = ?), ?), ?)
            """, (org_slug, project_slug, monthly_limit_usd, alert_threshold,
                  org_slug, project_slug, now, now))

    def record_spend(self, org_slug: str, project_slug: str, provider: str, model: str,
                    input_tokens: int, output_tokens: int, metadata: Dict[str, Any] = None) -> float:
        """
        Record spending for an API call.

        Args:
            org_slug: Organization slug
            project_slug: Project slug
            provider: Provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Optional additional data

        Returns:
            Cost in USD for this call

        Raises:
            KeyError: If provider/model pricing not found
        """
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        timestamp = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO spend_records
                (org_slug, project_slug, provider, model, input_tokens, output_tokens,
                 cost_usd, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (org_slug, project_slug, provider, model, input_tokens, output_tokens,
                  cost, timestamp, metadata_json))

        return cost

    def get_monthly_spend(self, org_slug: str, project_slug: str, month: datetime = None) -> float:
        """
        Get total spending for a month.

        Args:
            org_slug: Organization slug
            project_slug: Project slug
            month: Month to check (defaults to current month)

        Returns:
            Total spending in USD for the month
        """
        if month is None:
            month = datetime.utcnow()

        # Get start and end of month
        start_of_month = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month.month == 12:
            end_of_month = start_of_month.replace(year=month.year + 1, month=1)
        else:
            end_of_month = start_of_month.replace(month=month.month + 1)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COALESCE(SUM(cost_usd), 0)
                FROM spend_records
                WHERE org_slug = ? AND project_slug = ?
                AND timestamp >= ? AND timestamp < ?
            """, (org_slug, project_slug, start_of_month.isoformat(), end_of_month.isoformat()))

            return cursor.fetchone()[0]

    def get_budget_status(self, org_slug: str, project_slug: str) -> Dict[str, Any]:
        """
        Get budget status for an org/project.

        Args:
            org_slug: Organization slug
            project_slug: Project slug

        Returns:
            Dict with budget info and current spending
        """
        # Get budget limit
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT monthly_limit_usd, alert_threshold
                FROM budget_limits
                WHERE org_slug = ? AND project_slug = ?
            """, (org_slug, project_slug))

            budget_row = cursor.fetchone()
            if not budget_row:
                return {
                    "has_budget": False,
                    "monthly_limit_usd": None,
                    "current_spend_usd": 0.0,
                    "remaining_usd": None,
                    "percent_used": None,
                    "alert_triggered": False
                }

        monthly_limit, alert_threshold = budget_row
        current_spend = self.get_monthly_spend(org_slug, project_slug)
        remaining = monthly_limit - current_spend
        percent_used = current_spend / monthly_limit if monthly_limit > 0 else 0.0
        alert_triggered = percent_used >= alert_threshold

        return {
            "has_budget": True,
            "monthly_limit_usd": monthly_limit,
            "current_spend_usd": current_spend,
            "remaining_usd": remaining,
            "percent_used": percent_used,
            "alert_threshold": alert_threshold,
            "alert_triggered": alert_triggered,
            "over_budget": current_spend > monthly_limit
        }

    def check_budget_before_call(self, org_slug: str, project_slug: str, provider: str,
                                model: str, estimated_tokens: int) -> Dict[str, Any]:
        """
        Check if a potential API call would exceed budget.

        Args:
            org_slug: Organization slug
            project_slug: Project slug
            provider: Provider name
            model: Model name
            estimated_tokens: Estimated total tokens for the call

        Returns:
            Dict with approval status and budget info
        """
        try:
            # Estimate cost (assume 50/50 input/output split for simplicity)
            input_tokens = estimated_tokens // 2
            output_tokens = estimated_tokens - input_tokens
            estimated_cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        except KeyError:
            # If we don't have pricing, allow the call
            return {"approved": True, "reason": "pricing_not_available"}

        budget_status = self.get_budget_status(org_slug, project_slug)

        if not budget_status["has_budget"]:
            return {"approved": True, "reason": "no_budget_set", **budget_status}

        # Check if this call would exceed budget
        new_spend = budget_status["current_spend_usd"] + estimated_cost
        would_exceed = new_spend > budget_status["monthly_limit_usd"]

        return {
            "approved": not would_exceed,
            "reason": "would_exceed_budget" if would_exceed else "within_budget",
            "estimated_cost_usd": estimated_cost,
            "projected_spend_usd": new_spend,
            **budget_status
        }

    def get_spend_history(self, org_slug: str, project_slug: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get spending history for an org/project.

        Args:
            org_slug: Organization slug
            project_slug: Project slug
            days: Number of days to look back

        Returns:
            List of spending records
        """
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT provider, model, input_tokens, output_tokens,
                       cost_usd, timestamp, metadata
                FROM spend_records
                WHERE org_slug = ? AND project_slug = ?
                AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (org_slug, project_slug, cutoff))

            records = []
            for row in cursor.fetchall():
                provider, model, input_tokens, output_tokens, cost_usd, timestamp, metadata_json = row
                metadata = json.loads(metadata_json) if metadata_json else None

                records.append({
                    "provider": provider,
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost_usd": cost_usd,
                    "timestamp": timestamp,
                    "metadata": metadata
                })

            return records

    def list_budgets(self) -> List[Dict[str, Any]]:
        """
        List all budget configurations.

        Returns:
            List of budget configurations with current spend
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT org_slug, project_slug, monthly_limit_usd,
                       alert_threshold, created_at, updated_at
                FROM budget_limits
                ORDER BY org_slug, project_slug
            """)

            budgets = []
            for row in cursor.fetchall():
                org_slug, project_slug, monthly_limit_usd, alert_threshold, created_at, updated_at = row

                # Get current spend
                current_spend = self.get_monthly_spend(org_slug, project_slug)

                budgets.append({
                    "org_slug": org_slug,
                    "project_slug": project_slug,
                    "monthly_limit_usd": monthly_limit_usd,
                    "alert_threshold": alert_threshold,
                    "current_spend_usd": current_spend,
                    "remaining_usd": monthly_limit_usd - current_spend,
                    "percent_used": current_spend / monthly_limit_usd if monthly_limit_usd > 0 else 0.0,
                    "created_at": created_at,
                    "updated_at": updated_at
                })

            return budgets

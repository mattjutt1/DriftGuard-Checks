"""Tests for budget manager functionality."""

import json
import tempfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from promptops.budget import BudgetManager, BudgetLimit, SpendRecord


class TestBudgetManagerInit:
    """Test budget manager initialization and setup."""

    def test_init_with_default_paths(self):
        """Test budget manager initializes with default paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock XDG_DATA_HOME
            import os
            with pytest.MonkeyPatch.context() as mp:
                mp.setenv("XDG_DATA_HOME", temp_dir)

                manager = BudgetManager()

                # Should create database in XDG_DATA_HOME/promptops/
                expected_db = Path(temp_dir) / "promptops" / "budget.db"
                assert Path(manager.db_path) == expected_db

                # Database file should exist
                assert Path(manager.db_path).exists()

    def test_init_with_custom_paths(self):
        """Test budget manager with custom database and pricing paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "custom_budget.db"
            pricing_path = Path(temp_dir) / "custom_pricing.json"

            manager = BudgetManager(
                db_path=str(db_path),
                pricing_file=str(pricing_path)
            )

            assert manager.db_path == str(db_path)
            assert manager.pricing_file == str(pricing_path)
            assert db_path.exists()

    def test_database_tables_created(self):
        """Test that required database tables are created."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            manager = BudgetManager(db_path=temp_db.name)

            # Check that tables exist
            with sqlite3.connect(temp_db.name) as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name IN ('budget_limits', 'spend_records')
                """)
                tables = [row[0] for row in cursor.fetchall()]

                assert "budget_limits" in tables
                assert "spend_records" in tables

    def test_pricing_data_loaded(self):
        """Test that pricing data is loaded correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = BudgetManager(
                db_path=str(Path(temp_dir) / "test.db"),
                pricing_file=str(Path(temp_dir) / "pricing.json")
            )

            # Should have default pricing structure
            assert "providers" in manager.pricing
            assert "openai" in manager.pricing["providers"]
            assert "anthropic" in manager.pricing["providers"]

            # Check specific model pricing
            assert "gpt-4o-mini" in manager.pricing["providers"]["openai"]
            assert "claude-3-5-sonnet-20241022" in manager.pricing["providers"]["anthropic"]


class TestBudgetLimits:
    """Test budget limit functionality."""

    @pytest.fixture
    def manager(self):
        """Create a temporary budget manager for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield BudgetManager(db_path=temp_db.name)

    def test_set_budget(self, manager):
        """Test setting a budget limit."""
        manager.set_budget("org1", "project1", 100.0, 0.8)

        # Verify budget was set
        status = manager.get_budget_status("org1", "project1")
        assert status["has_budget"] is True
        assert status["monthly_limit_usd"] == 100.0
        assert status["alert_threshold"] == 0.8

    def test_budget_status_no_budget(self, manager):
        """Test budget status when no budget is set."""
        status = manager.get_budget_status("nonexistent", "project")

        assert status["has_budget"] is False
        assert status["monthly_limit_usd"] is None
        assert status["current_spend_usd"] == 0.0
        assert status["remaining_usd"] is None
        assert status["percent_used"] is None
        assert status["alert_triggered"] is False

    def test_update_existing_budget(self, manager):
        """Test updating an existing budget."""
        # Set initial budget
        manager.set_budget("org1", "project1", 100.0, 0.8)

        # Update budget
        manager.set_budget("org1", "project1", 200.0, 0.9)

        # Verify update
        status = manager.get_budget_status("org1", "project1")
        assert status["monthly_limit_usd"] == 200.0
        assert status["alert_threshold"] == 0.9

    def test_list_budgets_empty(self, manager):
        """Test listing budgets when none exist."""
        budgets = manager.list_budgets()
        assert budgets == []

    def test_list_budgets_with_data(self, manager):
        """Test listing budgets with existing data."""
        manager.set_budget("org1", "project1", 100.0)
        manager.set_budget("org2", "project2", 200.0)

        budgets = manager.list_budgets()
        assert len(budgets) == 2

        # Check budget details
        budget1 = next(b for b in budgets if b["org_slug"] == "org1")
        assert budget1["project_slug"] == "project1"
        assert budget1["monthly_limit_usd"] == 100.0
        assert budget1["current_spend_usd"] == 0.0


class TestCostCalculation:
    """Test cost calculation functionality."""

    @pytest.fixture
    def manager(self):
        """Create a temporary budget manager for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield BudgetManager(db_path=temp_db.name)

    def test_calculate_openai_cost(self, manager):
        """Test calculating cost for OpenAI models."""
        cost = manager.calculate_cost("openai", "gpt-4o-mini", 1000, 500)

        # Expected: (1000/1000 * 0.00015) + (500/1000 * 0.0006) = 0.00015 + 0.0003 = 0.00045
        assert cost == pytest.approx(0.00045, rel=1e-6)

    def test_calculate_anthropic_cost(self, manager):
        """Test calculating cost for Anthropic models."""
        cost = manager.calculate_cost("anthropic", "claude-3-5-sonnet-20241022", 1000, 500)

        # Expected: (1000/1000 * 0.003) + (500/1000 * 0.015) = 0.003 + 0.0075 = 0.0105
        assert cost == pytest.approx(0.0105, rel=1e-6)

    def test_calculate_cost_unknown_provider(self, manager):
        """Test calculating cost for unknown provider raises error."""
        with pytest.raises(KeyError):
            manager.calculate_cost("unknown", "model", 1000, 500)

    def test_calculate_cost_unknown_model(self, manager):
        """Test calculating cost for unknown model raises error."""
        with pytest.raises(KeyError):
            manager.calculate_cost("openai", "unknown-model", 1000, 500)


class TestSpendTracking:
    """Test spend tracking functionality."""

    @pytest.fixture
    def manager(self):
        """Create a temporary budget manager for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield BudgetManager(db_path=temp_db.name)

    def test_record_spend(self, manager):
        """Test recording a spend transaction."""
        cost = manager.record_spend("org1", "project1", "openai", "gpt-4o-mini", 1000, 500)

        # Verify cost calculation
        expected_cost = 0.00045  # As calculated above
        assert cost == pytest.approx(expected_cost, rel=1e-6)

        # Verify spend was recorded
        monthly_spend = manager.get_monthly_spend("org1", "project1")
        assert monthly_spend == pytest.approx(expected_cost, rel=1e-6)

    def test_record_spend_with_metadata(self, manager):
        """Test recording spend with metadata."""
        metadata = {"request_id": "req123", "user_id": "user456"}

        cost = manager.record_spend(
            "org1", "project1", "openai", "gpt-4o-mini",
            1000, 500, metadata=metadata
        )

        # Verify spend was recorded
        history = manager.get_spend_history("org1", "project1", days=1)
        assert len(history) == 1
        assert history[0]["metadata"] == metadata

    def test_multiple_spend_records(self, manager):
        """Test recording multiple spend transactions."""
        # Record multiple transactions
        cost1 = manager.record_spend("org1", "project1", "openai", "gpt-4o-mini", 1000, 500)
        cost2 = manager.record_spend("org1", "project1", "anthropic", "claude-3-5-sonnet-20241022", 800, 200)

        # Verify total spend
        monthly_spend = manager.get_monthly_spend("org1", "project1")
        expected_total = cost1 + cost2
        assert monthly_spend == pytest.approx(expected_total, rel=1e-6)

    def test_get_monthly_spend_different_months(self, manager):
        """Test monthly spend calculation for different months."""
        # Record spend for current month
        manager.record_spend("org1", "project1", "openai", "gpt-4o-mini", 1000, 500)

        # Get spend for current month
        current_spend = manager.get_monthly_spend("org1", "project1")
        assert current_spend > 0

        # Get spend for next month (should be 0)
        next_month = datetime.utcnow().replace(day=1)
        if next_month.month == 12:
            next_month = next_month.replace(year=next_month.year + 1, month=1)
        else:
            next_month = next_month.replace(month=next_month.month + 1)

        next_month_spend = manager.get_monthly_spend("org1", "project1", next_month)
        assert next_month_spend == 0

    def test_get_spend_history(self, manager):
        """Test getting spend history."""
        # Record multiple transactions
        manager.record_spend("org1", "project1", "openai", "gpt-4o-mini", 1000, 500)
        manager.record_spend("org1", "project1", "anthropic", "claude-3-5-sonnet-20241022", 800, 200)

        # Get history
        history = manager.get_spend_history("org1", "project1", days=30)

        assert len(history) == 2
        assert history[0]["provider"] in ["openai", "anthropic"]  # Most recent first
        assert "timestamp" in history[0]
        assert "cost_usd" in history[0]
        assert "input_tokens" in history[0]
        assert "output_tokens" in history[0]

    def test_get_spend_history_empty(self, manager):
        """Test getting spend history when no records exist."""
        history = manager.get_spend_history("nonexistent", "project")
        assert history == []


class TestBudgetEnforcement:
    """Test budget enforcement and alerts."""

    @pytest.fixture
    def manager(self):
        """Create a temporary budget manager for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield BudgetManager(db_path=temp_db.name)

    def test_budget_status_within_limits(self, manager):
        """Test budget status when within limits."""
        # Set budget and record small spend
        manager.set_budget("org1", "project1", 10.0, 0.8)  # $10 budget, 80% alert
        manager.record_spend("org1", "project1", "openai", "gpt-4o-mini", 1000, 500)  # ~$0.0005

        status = manager.get_budget_status("org1", "project1")

        assert status["has_budget"] is True
        assert status["monthly_limit_usd"] == 10.0
        assert status["current_spend_usd"] < 10.0
        assert status["remaining_usd"] > 0
        assert status["percent_used"] < 0.8
        assert status["alert_triggered"] is False
        assert status["over_budget"] is False

    def test_budget_status_alert_triggered(self, manager):
        """Test budget status when alert threshold is exceeded."""
        # Set small budget and record spend to trigger alert
        manager.set_budget("org1", "project1", 0.001, 0.5)  # $0.001 budget, 50% alert
        manager.record_spend("org1", "project1", "openai", "gpt-4o-mini", 2000, 1000)  # ~$0.0009

        status = manager.get_budget_status("org1", "project1")

        assert status["alert_triggered"] is True
        assert status["over_budget"] is False
        assert status["percent_used"] >= 0.5

    def test_budget_status_over_budget(self, manager):
        """Test budget status when budget is exceeded."""
        # Set very small budget and record large spend
        manager.set_budget("org1", "project1", 0.0001, 0.8)  # Very small budget
        manager.record_spend("org1", "project1", "anthropic", "claude-3-5-sonnet-20241022", 1000, 1000)

        status = manager.get_budget_status("org1", "project1")

        assert status["over_budget"] is True
        assert status["alert_triggered"] is True
        assert status["current_spend_usd"] > status["monthly_limit_usd"]
        assert status["remaining_usd"] < 0

    def test_check_budget_before_call_approved(self, manager):
        """Test budget check approves call within limits."""
        manager.set_budget("org1", "project1", 10.0)

        check_result = manager.check_budget_before_call(
            "org1", "project1", "openai", "gpt-4o-mini", 1000
        )

        assert check_result["approved"] is True
        assert check_result["reason"] == "within_budget"
        assert "estimated_cost_usd" in check_result

    def test_check_budget_before_call_would_exceed(self, manager):
        """Test budget check rejects call that would exceed budget."""
        # Set small budget and record spend close to limit
        manager.set_budget("org1", "project1", 0.001)
        manager.record_spend("org1", "project1", "openai", "gpt-4o-mini", 1000, 500)

        # Try to make a call that would exceed budget
        check_result = manager.check_budget_before_call(
            "org1", "project1", "anthropic", "claude-3-5-sonnet-20241022", 2000
        )

        assert check_result["approved"] is False
        assert check_result["reason"] == "would_exceed_budget"

    def test_check_budget_no_budget_set(self, manager):
        """Test budget check when no budget is configured."""
        check_result = manager.check_budget_before_call(
            "org1", "project1", "openai", "gpt-4o-mini", 1000
        )

        assert check_result["approved"] is True
        assert check_result["reason"] == "no_budget_set"

    def test_check_budget_unknown_pricing(self, manager):
        """Test budget check with unknown provider/model."""
        manager.set_budget("org1", "project1", 10.0)

        check_result = manager.check_budget_before_call(
            "org1", "project1", "unknown", "unknown-model", 1000
        )

        assert check_result["approved"] is True
        assert check_result["reason"] == "pricing_not_available"


class TestBudgetManagerEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def manager(self):
        """Create a temporary budget manager for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield BudgetManager(db_path=temp_db.name)

    def test_zero_token_cost(self, manager):
        """Test cost calculation with zero tokens."""
        cost = manager.calculate_cost("openai", "gpt-4o-mini", 0, 0)
        assert cost == 0.0

    def test_large_token_counts(self, manager):
        """Test cost calculation with large token counts."""
        # Test with 1M input and output tokens
        cost = manager.calculate_cost("openai", "gpt-4o-mini", 1_000_000, 1_000_000)
        expected = (1000 * 0.00015) + (1000 * 0.0006)  # $0.75
        assert cost == pytest.approx(expected, rel=1e-6)

    def test_negative_budget_limit(self, manager):
        """Test setting negative budget limit."""
        # Should not raise an error, but would be handled at application level
        manager.set_budget("org1", "project1", -100.0)
        status = manager.get_budget_status("org1", "project1")
        assert status["monthly_limit_usd"] == -100.0

    def test_zero_budget_limit(self, manager):
        """Test budget behavior with zero limit."""
        manager.set_budget("org1", "project1", 0.0)

        # Any spend should trigger over-budget
        manager.record_spend("org1", "project1", "openai", "gpt-4o-mini", 100, 50)

        status = manager.get_budget_status("org1", "project1")
        assert status["over_budget"] is True

    def test_unicode_org_project_names(self, manager):
        """Test budget system with unicode org/project names."""
        org = "组织机构"
        project = "项目名称"

        manager.set_budget(org, project, 100.0)
        manager.record_spend(org, project, "openai", "gpt-4o-mini", 1000, 500)

        status = manager.get_budget_status(org, project)
        assert status["has_budget"] is True
        assert status["current_spend_usd"] > 0

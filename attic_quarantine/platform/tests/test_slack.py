"""Tests for Slack notification helper."""

import os
import pytest
from unittest.mock import patch, Mock
from driftguard.alerts.slack import notify_slack, notify_slack_sync


class TestSlackNotifications:

    def setup_method(self):
        """Reset environment variables before each test."""
        for var in ["ALLOW_NETWORK", "SLACK_WEBHOOK_URL"]:
            if var in os.environ:
                del os.environ[var]

    def test_offline_mode_default(self):
        """Test that offline mode is the default behavior."""
        message = {"text": "Test alert"}
        result = notify_slack_sync(message)

        assert result["action"] == "logged_offline"
        assert result["status"] == "offline"
        assert result["network_allowed"] is False
        assert result["webhook_configured"] is False

    def test_offline_mode_explicit(self):
        """Test explicit offline mode."""
        os.environ["ALLOW_NETWORK"] = "0"
        os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/test"

        message = {"text": "Test alert"}
        result = notify_slack_sync(message)

        assert result["action"] == "logged_offline"
        assert result["status"] == "offline"
        assert result["network_allowed"] is False
        assert result["webhook_configured"] is True

    def test_no_webhook_url(self):
        """Test behavior when webhook URL is not configured."""
        os.environ["ALLOW_NETWORK"] = "1"

        message = {"text": "Test alert"}
        result = notify_slack_sync(message)

        assert result["action"] == "logged_offline"
        assert result["status"] == "offline"
        assert result["network_allowed"] is True
        assert result["webhook_configured"] is False

    @patch('requests.post')
    def test_successful_slack_post(self, mock_post):
        """Test successful Slack posting when network is allowed."""
        os.environ["ALLOW_NETWORK"] = "1"
        os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/test"

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        message = {"text": "Test alert"}
        result = notify_slack_sync(message)

        assert result["action"] == "posted_to_slack"
        assert result["status"] == "success"
        assert result["network_allowed"] is True
        assert result["webhook_configured"] is True

        # Verify the request was made
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["text"] == "Test alert"
        assert kwargs["json"]["username"] == "DriftGuard"
        assert kwargs["timeout"] == 10

    @patch('requests.post')
    def test_slack_api_error(self, mock_post):
        """Test handling of Slack API errors."""
        os.environ["ALLOW_NETWORK"] = "1"
        os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/test"

        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response

        message = {"text": "Test alert"}
        result = notify_slack_sync(message)

        assert result["action"] == "slack_error"
        assert result["status"] == "error"
        assert "Slack API returned 400" in result["error"]

    @patch('requests.post')
    def test_network_error(self, mock_post):
        """Test handling of network errors."""
        os.environ["ALLOW_NETWORK"] = "1"
        os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/test"

        # Mock network exception
        import requests
        mock_post.side_effect = requests.ConnectionError("Network unreachable")

        message = {"text": "Test alert"}
        result = notify_slack_sync(message)

        assert result["action"] == "network_error"
        assert result["status"] == "error"
        assert "Network unreachable" in result["error"]

    def test_message_structure(self):
        """Test that messages contain required fields."""
        message = {"text": "Test alert", "extra": "data"}
        result = notify_slack_sync(message)

        assert "timestamp" in result
        assert "message" in result
        assert result["message"] == message

    def test_complex_message_structure(self):
        """Test handling of complex Slack message structure."""
        message = {
            "text": "Alert with attachments",
            "attachments": [
                {
                    "color": "danger",
                    "fields": [
                        {"title": "Drift Score", "value": "0.85", "short": True}
                    ]
                }
            ]
        }

        result = notify_slack_sync(message)

        # Should work in offline mode
        assert result["action"] == "logged_offline"
        assert result["message"]["attachments"] == message["attachments"]

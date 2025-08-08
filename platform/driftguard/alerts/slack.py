"""Slack notification helper with offline mode support."""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import database dependencies
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from ..database import async_session_factory
    from ..models import Alert
    HAVE_DB = True
except ImportError:
    HAVE_DB = False
    logging.warning("Database imports failed, alerts will be logged only")

logger = logging.getLogger(__name__)


async def notify_slack(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send notification to Slack with offline mode support.

    Args:
        message: Slack message payload

    Returns:
        Dict with status and action taken
    """
    allow_network = os.getenv("ALLOW_NETWORK") == "1"
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "message": message,
        "network_allowed": allow_network,
        "webhook_configured": bool(webhook_url)
    }

    # Check if we should make network call
    if allow_network and webhook_url:
        try:
            import requests

            # Format message for Slack
            slack_payload = {
                "text": message.get("text", str(message)),
                "username": "DriftGuard",
                "icon_emoji": ":robot_face:"
            }

            # Add structured data if present
            if "attachments" in message:
                slack_payload["attachments"] = message["attachments"]

            # Make the request
            response = requests.post(
                webhook_url,
                json=slack_payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result["action"] = "posted_to_slack"
                result["status"] = "success"
                logger.info(f"Posted to Slack: {message.get('text', 'message')}")
            else:
                result["action"] = "slack_error"
                result["status"] = "error"
                result["error"] = f"Slack API returned {response.status_code}"
                logger.error(f"Slack API error {response.status_code}: {response.text}")

        except requests.RequestException as e:
            result["action"] = "network_error"
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"Network error posting to Slack: {e}")

        except ImportError:
            result["action"] = "requests_missing"
            result["status"] = "error"
            result["error"] = "requests library not available"
            logger.error("requests library not available for Slack notifications")

    else:
        # Offline mode - log and optionally store in database
        result["action"] = "logged_offline"
        result["status"] = "offline"

        log_msg = f"OFFLINE: Would post to Slack: {message.get('text', str(message))}"
        logger.info(log_msg)
        print(log_msg)  # Also print to stdout

        # Store in database if available
        if HAVE_DB:
            try:
                await _store_alert_in_db(message, result)
                result["db_stored"] = True
            except Exception as e:
                result["db_stored"] = False
                result["db_error"] = str(e)
                logger.warning(f"Failed to store alert in database: {e}")
        else:
            result["db_stored"] = False
            result["db_error"] = "database not available"

    return result


async def _store_alert_in_db(message: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Store alert in database for offline tracking."""
    if not HAVE_DB:
        return

    async with async_session_factory() as session:
        try:
            alert = Alert(
                eval_run_id=None,  # Not tied to specific eval run
                alert_type="slack_stub",
                severity="info",
                message=message.get("text", str(message)),
                meta={
                    "original_message": message,
                    "notification_result": result,
                    "offline_mode": True
                }
            )

            session.add(alert)
            await session.commit()
            logger.debug("Stored offline alert in database")

        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


def notify_slack_sync(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for notify_slack.

    For use in synchronous contexts like API endpoints.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(notify_slack(message))

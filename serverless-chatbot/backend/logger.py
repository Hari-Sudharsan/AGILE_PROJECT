"""
logger.py - Logging System
============================
Handles structured logging for the chatbot.

LOCAL:  Logs saved to data/app.log
CLOUD:  AWS CloudWatch automatically collects Lambda print/logging output

MLOps use: These logs help track what users ask, errors that occur,
and patterns that can be used to improve the chatbot.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# Log File Path
# ─────────────────────────────────────────────

LOG_DIR = os.path.join(os.path.dirname(__file__), "../data")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# ─────────────────────────────────────────────
# Python Logger Setup
# ─────────────────────────────────────────────

# Create data directory if it doesn't exist
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

# Configure Python's built-in logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),   # Save to file
        logging.StreamHandler()           # Also print to console
    ]
)

logger = logging.getLogger("chatbot")


# ─────────────────────────────────────────────
# Logging Functions
# ─────────────────────────────────────────────

def log_request(session_id: str, user_message: str):
    """
    Log every incoming chat request.
    This creates an audit trail and helps with debugging.

    In CloudWatch, you can search these logs using:
    filter @message like "REQUEST"
    """
    log_entry = {
        "type": "REQUEST",
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "message_length": len(user_message),
        "message_preview": user_message[:50] + "..." if len(user_message) > 50 else user_message
    }
    logger.info(json.dumps(log_entry))


def log_response(session_id: str, bot_response: str, response_time_ms: float):
    """
    Log bot responses with timing information.
    Helps identify slow responses (performance monitoring).
    """
    log_entry = {
        "type": "RESPONSE",
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "response_length": len(bot_response),
        "response_time_ms": response_time_ms
    }
    logger.info(json.dumps(log_entry))


def log_error(error_message: str, context: str = ""):
    """
    Log errors for debugging and alerting.

    In production, CloudWatch Alarms can trigger when error rate is high:
    - Send email notifications
    - Trigger auto-scaling
    - Create tickets in Jira/PagerDuty
    """
    log_entry = {
        "type": "ERROR",
        "timestamp": datetime.utcnow().isoformat(),
        "error": error_message,
        "context": context
    }
    logger.error(json.dumps(log_entry))


def log_model_version(version: str):
    """
    Log when a new model version is deployed.
    Helps track MLOps deployments over time.
    """
    log_entry = {
        "type": "MODEL_DEPLOY",
        "timestamp": datetime.utcnow().isoformat(),
        "model_version": version
    }
    logger.info(json.dumps(log_entry))


"""
─────────────────────────────────────────────
AWS CloudWatch Explanation for Students
─────────────────────────────────────────────

When your FastAPI runs on AWS Lambda:
- All print() and logging.info() output is automatically sent to CloudWatch
- CloudWatch stores these logs in "Log Groups"
- You can search, filter, and set alarms on these logs

Example CloudWatch Log Insights query to find slow responses:
    fields @timestamp, @message
    | filter @message like "RESPONSE"
    | filter response_time_ms > 2000
    | sort response_time_ms desc
    | limit 20

Example alarm: Alert if error rate > 5% in last 5 minutes
    → SNS notification → Email to developer
"""

"""
monitor.py - Monitoring & Metrics System
==========================================
Tracks key performance indicators (KPIs) for the chatbot.

This is the "Monitoring" part of MLOps:
- Response times (are we fast enough?)
- Error rates (are we reliable?)
- Request volume (how many users?)
- Model version distribution (which version is being used?)

LOCAL:  Metrics saved to data/metrics.json
CLOUD:  Use AWS CloudWatch Metrics (boto3) for dashboards & alarms
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# Metrics File Path
# ─────────────────────────────────────────────

METRICS_FILE = os.path.join(os.path.dirname(__file__), "../data/metrics.json")
Path(os.path.dirname(METRICS_FILE)).mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# Metrics Helper
# ─────────────────────────────────────────────

def load_metrics() -> dict:
    """Load current metrics from file"""
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f:
                return json.load(f)
        except:
            pass

    # Default metrics structure
    return {
        "total_requests": 0,
        "total_errors": 0,
        "total_response_time_ms": 0.0,
        "response_times": [],         # Keep last 100 for average
        "error_types": {},
        "requests_per_hour": {},
        "last_updated": ""
    }


def save_metrics(metrics: dict):
    """Save metrics to file"""
    metrics["last_updated"] = datetime.utcnow().isoformat()
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)


# ─────────────────────────────────────────────
# Tracking Functions
# ─────────────────────────────────────────────

def track_response_time(response_time_ms: float):
    """
    Record how long a response took.
    Used to identify performance bottlenecks.

    MLOps insight: If average response time increases after a model update,
    it means the new model is slower → consider rolling back.
    """
    metrics = load_metrics()

    metrics["total_requests"] += 1
    metrics["total_response_time_ms"] += response_time_ms

    # Keep only the last 100 response times
    metrics["response_times"].append(response_time_ms)
    if len(metrics["response_times"]) > 100:
        metrics["response_times"] = metrics["response_times"][-100:]

    # Track by hour (for traffic patterns)
    hour_key = datetime.utcnow().strftime("%Y-%m-%d %H:00")
    metrics["requests_per_hour"][hour_key] = metrics["requests_per_hour"].get(hour_key, 0) + 1

    save_metrics(metrics)

    # Optionally send to CloudWatch in production
    if os.getenv("ENVIRONMENT") == "production":
        send_to_cloudwatch("ResponseTime", response_time_ms, "Milliseconds")


def track_error(error_type: str):
    """
    Record errors with their type.
    High error rates indicate a problem that needs immediate attention.

    Common error types:
    - validation_error: User sent invalid input
    - server_error: Our code has a bug
    - api_error: External API (OpenAI) failed
    - db_error: Database connection issue
    """
    metrics = load_metrics()

    metrics["total_errors"] += 1

    # Count errors by type
    metrics["error_types"][error_type] = metrics["error_types"].get(error_type, 0) + 1

    save_metrics(metrics)

    if os.getenv("ENVIRONMENT") == "production":
        send_to_cloudwatch("ErrorCount", 1, "Count")


def get_metrics_summary() -> dict:
    """
    Generate a summary of current metrics.
    Can be exposed via an API endpoint for dashboards.
    """
    metrics = load_metrics()

    total_requests = metrics["total_requests"]
    total_errors = metrics["total_errors"]

    # Calculate averages
    avg_response_time = 0.0
    if metrics["response_times"]:
        avg_response_time = sum(metrics["response_times"]) / len(metrics["response_times"])

    error_rate = 0.0
    if total_requests > 0:
        error_rate = (total_errors / total_requests) * 100

    return {
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate_percent": round(error_rate, 2),
        "avg_response_time_ms": round(avg_response_time, 2),
        "error_types": metrics["error_types"],
        "last_updated": metrics.get("last_updated", "N/A")
    }


# ─────────────────────────────────────────────
# AWS CloudWatch Integration (Production)
# ─────────────────────────────────────────────

def send_to_cloudwatch(metric_name: str, value: float, unit: str):
    """
    Send a custom metric to AWS CloudWatch.

    In production, this lets you:
    1. Build dashboards showing response times
    2. Set alarms (e.g., alert if error rate > 10%)
    3. Auto-scale based on request volume

    This requires AWS permissions: cloudwatch:PutMetricData
    """
    try:
        import boto3
        cloudwatch = boto3.client("cloudwatch", region_name=os.getenv("AWS_REGION", "us-east-1"))

        cloudwatch.put_metric_data(
            Namespace="ChatbotMLOps",    # Group your metrics under this namespace
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit,
                    "Dimensions": [
                        {
                            "Name": "Environment",
                            "Value": os.getenv("ENVIRONMENT", "local")
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        # Don't crash the app if CloudWatch fails
        print(f"CloudWatch metric send failed: {e}")

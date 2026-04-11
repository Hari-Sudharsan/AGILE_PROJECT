"""
database.py - Database Integration Layer
==========================================
This module handles all database operations.

LOCAL (Development):  SQLite — a simple file-based database
CLOUD (Production):   AWS DynamoDB — a serverless NoSQL database

The ENVIRONMENT variable controls which one to use.
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/chatbot.db")
DYNAMO_TABLE = os.getenv("DB_TABLE_NAME", "ChatLogs")

# ─────────────────────────────────────────────
# Table Schema (conceptual — same for both DBs)
# ─────────────────────────────────────────────
"""
TABLE: ChatLogs
┌─────────────────┬──────────────┬─────────────────────────────────────┐
│ Field           │ Type         │ Description                         │
├─────────────────┼──────────────┼─────────────────────────────────────┤
│ id              │ TEXT (PK)    │ Unique UUID for each log entry      │
│ session_id      │ TEXT         │ Groups messages in one conversation │
│ user_message    │ TEXT         │ What the user typed                 │
│ bot_response    │ TEXT         │ What the bot replied                │
│ timestamp       │ TEXT         │ ISO 8601 UTC timestamp              │
│ model_version   │ TEXT         │ Which model version responded       │
│ response_time   │ REAL         │ How long the response took (ms)     │
└─────────────────┴──────────────┴─────────────────────────────────────┘
"""


# ─────────────────────────────────────────────
# SQLite (Local Database)
# ─────────────────────────────────────────────

def init_sqlite():
    """Create the SQLite database and table if they don't exist"""
    # Make sure the data directory exists
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ChatLogs (
            id            TEXT PRIMARY KEY,
            session_id    TEXT NOT NULL,
            user_message  TEXT NOT NULL,
            bot_response  TEXT NOT NULL,
            timestamp     TEXT NOT NULL,
            model_version TEXT NOT NULL,
            response_time REAL DEFAULT 0.0
        )
    """)

    conn.commit()
    conn.close()
    print("✅ SQLite database initialized")


def save_to_sqlite(session_id, user_message, bot_response, timestamp, model_version, response_time=0.0):
    """Save a chat log entry to SQLite"""
    init_sqlite()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    entry_id = str(uuid.uuid4())  # Generate unique ID

    cursor.execute("""
        INSERT INTO ChatLogs (id, session_id, user_message, bot_response, timestamp, model_version, response_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (entry_id, session_id, user_message, bot_response, timestamp, model_version, response_time))

    conn.commit()
    conn.close()
    print(f"✅ Saved to SQLite: {entry_id}")


def get_from_sqlite(session_id):
    """Retrieve chat history for a session from SQLite"""
    init_sqlite()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, bot_response, timestamp, model_version
        FROM ChatLogs
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()

    # Convert to list of dicts
    return [
        {
            "user_message": row[0],
            "bot_response": row[1],
            "timestamp": row[2],
            "model_version": row[3]
        }
        for row in rows
    ]


# ─────────────────────────────────────────────
# DynamoDB (AWS Cloud Database)
# ─────────────────────────────────────────────

def save_to_dynamodb(session_id, user_message, bot_response, timestamp, model_version, response_time=0.0):
    """
    Save a chat log entry to AWS DynamoDB.

    DynamoDB is AWS's serverless NoSQL database.
    It scales automatically and charges only for what you use.

    boto3 is the official AWS SDK for Python.
    """
    import boto3
    from decimal import Decimal

    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = dynamodb.Table(DYNAMO_TABLE)

    entry_id = str(uuid.uuid4())

    # DynamoDB item (same structure as SQLite)
    item = {
        "id": entry_id,
        "session_id": session_id,
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": timestamp,
        "model_version": model_version,
        "response_time": Decimal(str(response_time))  # DynamoDB uses Decimal for floats
    }

    table.put_item(Item=item)
    print(f"✅ Saved to DynamoDB: {entry_id}")


def get_from_dynamodb(session_id):
    """
    Query chat history from DynamoDB.

    We use a 'query' operation with a filter (scan in this simple version).
    In production, add a GSI (Global Secondary Index) on session_id for faster queries.
    """
    import boto3
    from boto3.dynamodb.conditions import Attr

    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = dynamodb.Table(DYNAMO_TABLE)

    response = table.scan(
        FilterExpression=Attr("session_id").eq(session_id)
    )

    items = response.get("Items", [])
    # Sort by timestamp
    items.sort(key=lambda x: x.get("timestamp", ""))

    return [
        {
            "user_message": item["user_message"],
            "bot_response": item["bot_response"],
            "timestamp": item["timestamp"],
            "model_version": item["model_version"]
        }
        for item in items
    ]


# ─────────────────────────────────────────────
# Public Interface (Routes to correct DB)
# ─────────────────────────────────────────────

def save_chat_log(session_id, user_message, bot_response, timestamp, model_version, response_time=0.0):
    """
    Save a chat log.
    Automatically uses SQLite (local) or DynamoDB (AWS) based on ENVIRONMENT.
    """
    # Also save to JSON for MLOps data collection
    save_to_json_log(session_id, user_message, bot_response, timestamp, model_version)

    if ENVIRONMENT == "production":
        save_to_dynamodb(session_id, user_message, bot_response, timestamp, model_version, response_time)
    else:
        save_to_sqlite(session_id, user_message, bot_response, timestamp, model_version, response_time)


def get_chat_history(session_id):
    """
    Retrieve chat history.
    Automatically uses SQLite (local) or DynamoDB (AWS) based on ENVIRONMENT.
    """
    if ENVIRONMENT == "production":
        return get_from_dynamodb(session_id)
    else:
        return get_from_sqlite(session_id)


# ─────────────────────────────────────────────
# MLOps: JSON Log (always saved — used for training data)
# ─────────────────────────────────────────────

def save_to_json_log(session_id, user_message, bot_response, timestamp, model_version):
    """
    Save all chats to a JSON file.
    This is the 'data collection' part of MLOps.
    Later, these logs can be used to retrain/improve the model.
    """
    log_path = os.path.join(os.path.dirname(__file__), "../data/chat_logs.json")
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    # Load existing logs
    logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                logs = json.load(f)
        except:
            logs = []

    # Add new entry
    logs.append({
        "session_id": session_id,
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": timestamp,
        "model_version": model_version
    })

    # Save back
    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2)

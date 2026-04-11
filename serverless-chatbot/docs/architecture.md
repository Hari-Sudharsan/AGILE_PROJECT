# Architecture & Deployment Guide

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SERVERLESS CHATBOT ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   USER'S BROWSER                                                            │
│   ┌──────────────────┐                                                      │
│   │   React App      │  Static files served from S3                        │
│   │  (Chat UI)       │◄────────────────────────────── AWS S3 Bucket        │
│   │                  │                                 (Static Website)     │
│   └────────┬─────────┘                                                      │
│            │ HTTPS POST /chat                                               │
│            ▼                                                                │
│   ┌──────────────────┐                                                      │
│   │  AWS API Gateway │  ← Entry point for all API calls                    │
│   │  (REST API)      │    Handles: Auth, Rate Limiting, CORS               │
│   └────────┬─────────┘                                                      │
│            │ Trigger                                                        │
│            ▼                                                                │
│   ┌──────────────────┐     ┌─────────────────┐                             │
│   │  AWS Lambda      │────►│  FastAPI + Mangum│                            │
│   │  (Serverless)    │     │  (Python 3.11)   │                            │
│   │  Auto-scales!    │     └────────┬─────────┘                            │
│   └──────────────────┘             │                                       │
│                                    │                                        │
│            ┌───────────────────────┼──────────────────────┐                │
│            ▼                       ▼                       ▼                │
│   ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐       │
│   │  AWS DynamoDB   │   │  AWS CloudWatch  │   │  AWS S3 (Logs)  │       │
│   │  (Chat Logs DB) │   │  (Logs + Metrics)│   │  (Chat Log JSON)│       │
│   └─────────────────┘   └──────────────────┘   └──────────────────┘       │
│                                                                             │
│   MLOPS LAYER (runs separately / scheduled)                                │
│   ┌──────────────────────────────────────────────────────┐                 │
│   │  Training Script → Evaluation → Version Update       │                 │
│   │  (ml/train.py)    (ml/evaluate.py) (ml/version.txt) │                 │
│   └──────────────────────────────────────────────────────┘                 │
│                                                                             │
│   CI/CD (GitHub Actions)                                                   │
│   ┌──────────────────────────────────────────────────────┐                 │
│   │  Git Push → Test → Build → Deploy Lambda + S3        │                 │
│   └──────────────────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Component Diagram

```
┌─────────────────────────────────────────────────┐
│              FRONTEND (React)                   │
│  App.js                                         │
│    ├── ChatWindow.js  (message display)         │
│    │     └── MessageBubble.js (per message)     │
│    └── InputBar.js    (text input + send btn)   │
└─────────────────────────────────────────────────┘
                    │ HTTP POST /chat
┌─────────────────────────────────────────────────┐
│              BACKEND (FastAPI)                  │
│  main.py          (routes & orchestration)      │
│    ├── chat_handler.py  (bot logic / LLM)       │
│    ├── database.py      (SQLite / DynamoDB)     │
│    ├── logger.py        (structured logging)    │
│    └── monitor.py       (metrics tracking)      │
│  lambda_handler.py  (AWS Lambda adapter)        │
└─────────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────────┐
│              MLOPS LAYER                        │
│  ml/train.py      (training pipeline)           │
│  ml/evaluate.py   (performance evaluation)      │
│  ml/version.txt   (current model version)       │
└─────────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────────┐
│              DATA LAYER                         │
│  data/chatbot.db      (SQLite — local)          │
│  data/chat_logs.json  (MLOps training data)     │
│  data/metrics.json    (performance metrics)     │
│  data/app.log         (application logs)        │
└─────────────────────────────────────────────────┘
```

## 3. Database Schema

### Table: ChatLogs

| Field          | Type    | Constraint | Description                            |
|----------------|---------|------------|----------------------------------------|
| id             | TEXT    | PRIMARY KEY| UUID — unique identifier per log entry |
| session_id     | TEXT    | NOT NULL   | Groups messages in one conversation    |
| user_message   | TEXT    | NOT NULL   | The message typed by the user          |
| bot_response   | TEXT    | NOT NULL   | The chatbot's reply                    |
| timestamp      | TEXT    | NOT NULL   | ISO 8601 UTC (e.g. 2024-01-01T10:00Z) |
| model_version  | TEXT    | NOT NULL   | Which model version responded (e.g. 1.0.2) |
| response_time  | REAL    | DEFAULT 0  | Response latency in milliseconds       |

**DynamoDB equivalent:**
- Partition Key: `id` (String)
- GSI (Global Secondary Index): `session_id` for efficient history queries
- All other fields stored as DynamoDB attributes

## 4. AWS Step-by-Step Deployment

### Step 1 — Create DynamoDB Table
```
1. Go to AWS Console → DynamoDB → Create Table
2. Table name: ChatLogs
3. Partition key: id (String)
4. Click Create
```

### Step 2 — Create Lambda Function
```
1. Go to AWS Console → Lambda → Create Function
2. Name: serverless-chatbot
3. Runtime: Python 3.11
4. Create function
5. Upload the backend ZIP (see CI/CD section)
6. Handler: lambda_handler.handler
```

### Step 3 — Set Lambda Environment Variables
```
ENVIRONMENT        = production
DB_TABLE_NAME      = ChatLogs
AWS_REGION         = us-east-1
MODEL_VERSION      = 1.0.0
OPENAI_API_KEY     = (optional)
```

### Step 4 — Create API Gateway
```
1. Go to API Gateway → Create API → REST API
2. Create resource: /chat
3. Create method: POST
4. Integration type: Lambda Function
5. Select your Lambda
6. Deploy to stage: prod
7. Copy the Invoke URL
```

### Step 5 — Create S3 Bucket for Frontend
```
1. Go to S3 → Create Bucket
2. Name: my-chatbot-frontend (must be globally unique)
3. Uncheck "Block all public access"
4. Enable Static Website Hosting
5. Index document: index.html
6. Upload build/ files (npm run build first)
```

### Step 6 — Update Frontend API URL
Before building, set in frontend/.env.production:
```
REACT_APP_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
```

### Step 7 — Test
```bash
curl -X POST https://YOUR_API_URL/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test-001"}'
```

## 5. CloudWatch Monitoring

After deployment, CloudWatch automatically collects Lambda logs.

**Useful Log Insights queries:**

```sql
-- Find all errors in last 1 hour
fields @timestamp, @message
| filter @message like "ERROR"
| sort @timestamp desc
| limit 50

-- Average response time
fields @timestamp, @message
| filter @message like "RESPONSE"
| parse @message '"response_time_ms": *,' as rt
| stats avg(rt) as avg_ms

-- Requests per hour
fields @timestamp
| filter @message like "REQUEST"
| stats count() as requests by bin(1h)
```

**Set up CloudWatch Alarm:**
1. CloudWatch → Alarms → Create Alarm
2. Select metric: Lambda → Errors
3. Threshold: > 10 errors in 5 minutes
4. Action: Send email via SNS

## 6. MLOps Pipeline Explanation

```
DATA COLLECTION
    │  Every chat is saved to:
    │  - SQLite/DynamoDB (structured)
    │  - chat_logs.json (raw, for training)
    ▼
ANALYSIS (evaluate.py)
    │  Checks: volume, patterns, errors
    │  Decides: is retraining needed?
    ▼
TRAINING (train.py)
    │  Loads chat logs
    │  Simulates fine-tuning
    │  Tracks loss/accuracy per epoch
    ▼
QUALITY GATE
    │  If accuracy > 80% → proceed
    │  If not → keep current version
    ▼
VERSION UPDATE (version.txt)
    │  Bumps patch version: 1.0.0 → 1.0.1
    │  Logged in training_report.json
    ▼
DEPLOY
    GitHub Actions detects new version
    → Deploys updated Lambda function
    → New model_version appears in API responses
```

## 7. Sample Log Output

```json
{"type": "REQUEST",  "timestamp": "2024-01-15T10:23:45.123Z", "session_id": "session-abc123", "message_length": 12, "message_preview": "Hello there!"}
{"type": "RESPONSE", "timestamp": "2024-01-15T10:23:45.389Z", "session_id": "session-abc123", "response_length": 42, "response_time_ms": 265.4}
{"type": "REQUEST",  "timestamp": "2024-01-15T10:24:01.000Z", "session_id": "session-abc123", "message_length": 15, "message_preview": "Tell me a joke"}
{"type": "RESPONSE", "timestamp": "2024-01-15T10:24:01.210Z", "session_id": "session-abc123", "response_length": 68, "response_time_ms": 209.1}
{"type": "ERROR",    "timestamp": "2024-01-15T10:25:00.000Z", "error": "Message too long (max 500 characters)", "context": ""}
```

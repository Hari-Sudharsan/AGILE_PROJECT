# 🤖 Serverless Chatbot with MLOps Pipeline

A complete college-level project demonstrating a serverless chatbot application with MLOps and DevOps practices, deployable on AWS.

---

## 📌 Project Overview

This project builds a simple but production-ready chatbot that:
- Runs **locally** for development
- Deploys to **AWS** (Lambda + API Gateway + S3 + DynamoDB)
- Demonstrates **MLOps** practices (data collection, versioning, monitoring)
- Uses **GitHub Actions** for CI/CD automation

---

## ✨ Features

- 💬 React-based Chat UI with real-time responses
- ⚡ FastAPI backend (serverless-compatible)
- 🧠 Pluggable chatbot logic (rule-based or LLM API)
- 🗄️ SQLite (local) / DynamoDB (cloud) storage
- 📊 MLOps: data collection, model versioning, monitoring
- 🔁 CI/CD: GitHub Actions pipeline
- 🔐 Secure: input validation, env variables, error handling
- ☁️ AWS: Lambda, API Gateway, S3, DynamoDB, CloudWatch

---

## 🛠️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | React 18, Axios, CSS              |
| Backend    | Python 3.11, FastAPI, Mangum      |
| Database   | SQLite (local), DynamoDB (cloud)  |
| MLOps      | Custom scripts, JSON logs         |
| DevOps     | GitHub Actions, Docker (optional) |
| Cloud      | AWS Lambda, API Gateway, S3       |
| Monitoring | CloudWatch, local logs            |

---

## 📁 Project Structure

```
serverless-chatbot/
├── frontend/               # React chat UI
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── components/
│   │   │   ├── ChatWindow.js
│   │   │   ├── MessageBubble.js
│   │   │   └── InputBar.js
│   │   └── index.js
│   └── package.json
├── backend/                # FastAPI backend
│   ├── main.py             # FastAPI app entry
│   ├── chat_handler.py     # Chat logic
│   ├── database.py         # DB operations (SQLite/DynamoDB)
│   ├── logger.py           # Logging system
│   ├── monitor.py          # Monitoring & metrics
│   ├── requirements.txt
│   └── lambda_handler.py   # AWS Lambda entry point
├── ml/                     # MLOps scripts
│   ├── train.py            # Simulated training script
│   ├── version.txt         # Model version tracker
│   └── evaluate.py         # Model evaluation
├── data/                   # Data storage
│   ├── chat_logs.json      # Chat history logs
│   ├── chatbot.db          # SQLite database
│   └── metrics.json        # Monitoring metrics
├── tests/                  # Test suite
│   ├── test_api.py
│   ├── test_chat.py
│   └── test_database.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # GitHub Actions pipeline
├── docs/
│   ├── architecture.md
│   └── deployment-guide.md
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/serverless-chatbot.git
cd serverless-chatbot
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env     # Edit .env with your values
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

---

## ▶️ How to Run Locally

**Start Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```
Backend runs at: `http://localhost:8000`
API Docs at: `http://localhost:8000/docs`

**Start Frontend (Terminal 2):**
```bash
cd frontend
npm start
```
Frontend runs at: `http://localhost:3000`

---

## ☁️ AWS Deployment Steps

### Step 1: Deploy Backend to AWS Lambda

```bash
# Install Zappa or use AWS SAM
pip install zappa
zappa init
zappa deploy production
```

Or manually:
1. Zip backend folder: `zip -r backend.zip backend/`
2. Go to AWS Lambda → Create Function
3. Upload `backend.zip`
4. Set handler: `lambda_handler.handler`
5. Set runtime: Python 3.11

### Step 2: Configure API Gateway
1. Go to AWS API Gateway
2. Create REST API
3. Create resource `/chat` with POST method
4. Connect to Lambda function
5. Deploy to stage (e.g., `prod`)
6. Copy the Invoke URL

### Step 3: Host Frontend on S3
```bash
cd frontend
npm run build
aws s3 sync build/ s3://your-bucket-name --acl public-read
```
Enable Static Website Hosting in S3 bucket settings.

### Step 4: Set Environment Variables
In Lambda → Configuration → Environment Variables:
- `OPENAI_API_KEY` = your_key
- `DB_TABLE_NAME` = ChatLogs
- `MODEL_VERSION` = 1.0.0
- `ENVIRONMENT` = production

### Step 5: Test Deployed API
```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

---

## 🔁 CI/CD Pipeline

The GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) runs automatically on every push:

| Stage  | What it does                                |
|--------|---------------------------------------------|
| Build  | Install dependencies, lint code             |
| Test   | Run all unit & functional tests             |
| Deploy | Deploy to AWS Lambda + S3 (on main branch)  |

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`
- `LAMBDA_FUNCTION_NAME`

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v --tb=short
```

---

## 🔮 Future Improvements

- [ ] Add real LLM (GPT-4 / Claude API)
- [ ] User authentication (JWT)
- [ ] Conversation context/memory
- [ ] Auto model retraining pipeline
- [ ] Response caching with Redis
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Analytics dashboard
- [ ] A/B testing for model versions
- [ ] Rate limiting per user

---

## 👨‍🎓 Academic Context

This project was built as a college-level demonstration of:
- Full-stack development
- Cloud computing (AWS)
- MLOps practices
- DevOps/CI-CD automation
- Software testing

---

## 📄 License

MIT License - free for educational use.

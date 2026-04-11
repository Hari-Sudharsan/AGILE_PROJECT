"""
lambda_handler.py - AWS Lambda Entry Point
============================================
Mangum is an adapter that wraps FastAPI so it can run inside AWS Lambda.
When AWS Lambda receives an HTTP request from API Gateway, it calls handler().
Mangum translates the Lambda event format → ASGI (what FastAPI understands).

Usage:
  In AWS Lambda settings, set handler to: lambda_handler.handler
"""

from mangum import Mangum
from main import app

# Wrap the FastAPI app with Mangum adapter
# This makes FastAPI work like an AWS Lambda function
handler = Mangum(app, lifespan="off")

"""
How it works:

  API Gateway
      │
      ▼ (HTTP Request as JSON event)
  AWS Lambda
      │
      ▼
  Mangum (adapter)
      │
      ▼
  FastAPI app (same code as local)
      │
      ▼
  Response → back to API Gateway → back to user
"""

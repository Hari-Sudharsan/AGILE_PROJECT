"""
ml/train.py - Simulated Model Training Script
===============================================
In a real MLOps system, this script would:
1. Load collected chat data
2. Fine-tune the language model on new patterns
3. Evaluate the new model
4. If better, update version.txt and deploy

Here, we SIMULATE this process to demonstrate the concept.
This is a key part of the MLOps lifecycle.

How to run: python ml/train.py
"""

import json
import os
import time
import random
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
VERSION_FILE = os.path.join(os.path.dirname(__file__), "version.txt")
CHAT_LOGS = os.path.join(DATA_DIR, "chat_logs.json")
TRAINING_REPORT = os.path.join(DATA_DIR, "training_report.json")


# ─────────────────────────────────────────────
# Step 1: Data Collection
# ─────────────────────────────────────────────

def load_training_data():
    """
    Load collected chat logs for training.
    In real MLOps, this would pull from S3 or a data warehouse.
    """
    print("\n📊 STEP 1: Loading Training Data")
    print("─" * 40)

    if not os.path.exists(CHAT_LOGS):
        print("⚠️  No chat logs found. Creating sample data...")
        sample_data = [
            {"user_message": "hello", "bot_response": "Hello! How can I help?", "timestamp": "2024-01-01T10:00:00Z"},
            {"user_message": "bye", "bot_response": "Goodbye! Have a great day!", "timestamp": "2024-01-01T10:01:00Z"},
            {"user_message": "what is ai", "bot_response": "AI is artificial intelligence!", "timestamp": "2024-01-01T10:02:00Z"},
        ]
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
        with open(CHAT_LOGS, "w") as f:
            json.dump(sample_data, f, indent=2)
        return sample_data

    with open(CHAT_LOGS, "r") as f:
        data = json.load(f)

    print(f"✅ Loaded {len(data)} chat records")
    return data


# ─────────────────────────────────────────────
# Step 2: Data Analysis
# ─────────────────────────────────────────────

def analyze_data(data: list) -> dict:
    """
    Analyze the training data to understand patterns.
    In a real system, this would identify:
    - Common unanswered questions (gaps in model knowledge)
    - Frequently used topics (focus areas)
    - Error patterns (failure modes)
    """
    print("\n🔍 STEP 2: Analyzing Training Data")
    print("─" * 40)

    total = len(data)
    avg_message_len = sum(len(d.get("user_message", "")) for d in data) / max(total, 1)

    # Simulate topic distribution
    topics = {
        "greetings": random.randint(20, 40),
        "questions": random.randint(30, 50),
        "farewells": random.randint(10, 20),
        "other": random.randint(5, 15)
    }

    stats = {
        "total_samples": total,
        "avg_message_length": round(avg_message_len, 2),
        "topic_distribution": topics
    }

    print(f"  Total samples: {total}")
    print(f"  Avg message length: {avg_message_len:.1f} chars")
    print(f"  Topic distribution: {topics}")

    return stats


# ─────────────────────────────────────────────
# Step 3: Simulated Training
# ─────────────────────────────────────────────

def train_model(data: list, stats: dict) -> dict:
    """
    Simulate model training with a progress bar.

    In reality, this would:
    - Run fine-tuning on GPT/BERT/custom model
    - Use GPU computing
    - Track loss metrics
    - Run for hours/days
    """
    print("\n🧠 STEP 3: Training Model (Simulated)")
    print("─" * 40)

    epochs = 5
    results = {"epoch_losses": [], "final_accuracy": 0}

    for epoch in range(1, epochs + 1):
        # Simulate decreasing loss (model improving)
        loss = round(1.0 - (epoch * 0.15) + random.uniform(-0.05, 0.05), 4)
        accuracy = round(0.5 + (epoch * 0.08) + random.uniform(-0.02, 0.02), 4)

        print(f"  Epoch {epoch}/{epochs} | Loss: {loss:.4f} | Accuracy: {accuracy:.4f}")
        results["epoch_losses"].append(loss)

        time.sleep(0.3)  # Simulate training time

    results["final_accuracy"] = round(0.85 + random.uniform(0, 0.1), 4)
    print(f"\n  ✅ Training complete! Final Accuracy: {results['final_accuracy']:.4f}")

    return results


# ─────────────────────────────────────────────
# Step 4: Model Evaluation
# ─────────────────────────────────────────────

def evaluate_model(training_results: dict) -> bool:
    """
    Decide if the new model is good enough to deploy.
    This is called the "Model Quality Gate".

    If the new model performs worse than the current one,
    we should NOT deploy it (this prevents model degradation).
    """
    print("\n📏 STEP 4: Evaluating Model")
    print("─" * 40)

    # Simulated evaluation metrics
    metrics = {
        "accuracy": training_results["final_accuracy"],
        "precision": round(random.uniform(0.80, 0.95), 4),
        "recall": round(random.uniform(0.75, 0.92), 4),
        "f1_score": round(random.uniform(0.78, 0.93), 4),
    }

    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1_score']:.4f}")

    # Quality gate: deploy only if accuracy > 0.80
    deploy = metrics["accuracy"] > 0.80
    print(f"\n  Quality Gate (accuracy > 0.80): {'✅ PASSED' if deploy else '❌ FAILED'}")

    return deploy, metrics


# ─────────────────────────────────────────────
# Step 5: Version Tracking
# ─────────────────────────────────────────────

def update_version():
    """
    Increment the model version number.
    This is critical for MLOps — always track which version is deployed!

    Version format: MAJOR.MINOR.PATCH
    - MAJOR: Breaking changes
    - MINOR: New features
    - PATCH: Bug fixes / improvements
    """
    print("\n🏷️  STEP 5: Updating Model Version")
    print("─" * 40)

    # Read current version
    current_version = "1.0.0"
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            current_version = f.read().strip()

    # Increment patch version
    parts = current_version.split(".")
    parts[2] = str(int(parts[2]) + 1)
    new_version = ".".join(parts)

    # Save new version
    with open(VERSION_FILE, "w") as f:
        f.write(new_version)

    print(f"  Previous version: {current_version}")
    print(f"  New version:      {new_version}")
    print(f"  Saved to:         {VERSION_FILE}")

    return new_version


# ─────────────────────────────────────────────
# Step 6: Save Training Report
# ─────────────────────────────────────────────

def save_training_report(stats, training_results, metrics, new_version, deployed):
    """Save a full training report for audit trail"""
    report = {
        "training_date": datetime.utcnow().isoformat(),
        "new_version": new_version,
        "deployed": deployed,
        "data_stats": stats,
        "training_results": training_results,
        "evaluation_metrics": metrics
    }

    with open(TRAINING_REPORT, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Training report saved to: {TRAINING_REPORT}")


# ─────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────

def run_training_pipeline():
    """
    Run the complete MLOps training pipeline.
    This is the main function that orchestrates all steps.

    In production, this would be triggered by:
    - A scheduled job (e.g., weekly retraining)
    - A CI/CD pipeline trigger
    - Enough new data being collected
    - Model performance dropping below threshold
    """
    print("=" * 50)
    print("  🤖 MLOps Training Pipeline")
    print(f"  Started: {datetime.utcnow().isoformat()}")
    print("=" * 50)

    # Run all steps
    data = load_training_data()
    stats = analyze_data(data)
    training_results = train_model(data, stats)
    deploy, metrics = evaluate_model(training_results)

    if deploy:
        new_version = update_version()
        save_training_report(stats, training_results, metrics, new_version, True)

        print("\n" + "=" * 50)
        print(f"  ✅ PIPELINE COMPLETE!")
        print(f"  New model version {new_version} is ready!")
        print(f"  Next: Deploy to AWS Lambda")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("  ❌ Model did not pass quality gate.")
        print("  Current version remains in production.")
        print("=" * 50)
        save_training_report(stats, training_results, metrics, "unchanged", False)


if __name__ == "__main__":
    run_training_pipeline()

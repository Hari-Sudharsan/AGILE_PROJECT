"""
ml/evaluate.py - Model Evaluation Script
==========================================
Analyzes collected chat logs to measure chatbot performance.
Run this periodically to check if the model needs retraining.

How to run: python ml/evaluate.py
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
CHAT_LOGS = os.path.join(DATA_DIR, "chat_logs.json")
METRICS_FILE = os.path.join(DATA_DIR, "metrics.json")


def load_data():
    if not os.path.exists(CHAT_LOGS):
        print("⚠️  No chat logs found. Run the chatbot first to collect data.")
        return []
    with open(CHAT_LOGS, "r") as f:
        return json.load(f)


def evaluate():
    """Run full evaluation and print report"""
    print("=" * 50)
    print("  📊 Model Evaluation Report")
    print(f"  Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)

    data = load_data()
    if not data:
        return

    total = len(data)
    print(f"\n📁 Total chat records: {total}")

    # ── Version distribution ──────────────────────────────
    versions = {}
    for entry in data:
        v = entry.get("model_version", "unknown")
        versions[v] = versions.get(v, 0) + 1

    print("\n🏷️  Model Version Distribution:")
    for ver, count in sorted(versions.items()):
        pct = round(count / total * 100, 1)
        bar = "█" * int(pct / 5)
        print(f"   v{ver}: {bar} {count} ({pct}%)")

    # ── Recent activity ───────────────────────────────────
    now = datetime.utcnow()
    recent = [
        e for e in data
        if (now - datetime.fromisoformat(e["timestamp"].replace("Z", ""))).days < 7
    ]
    print(f"\n📅 Last 7 days: {len(recent)} messages")

    # ── Response length analysis ──────────────────────────
    response_lengths = [len(e.get("bot_response", "")) for e in data]
    avg_len = sum(response_lengths) / len(response_lengths) if response_lengths else 0
    print(f"\n💬 Avg bot response length: {avg_len:.0f} characters")

    # ── Monitoring metrics ────────────────────────────────
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            metrics = json.load(f)
        print(f"\n📈 Performance Metrics:")
        print(f"   Total requests:   {metrics.get('total_requests', 0)}")
        print(f"   Total errors:     {metrics.get('total_errors', 0)}")
        rt = metrics.get("response_times", [])
        if rt:
            print(f"   Avg response time: {sum(rt)/len(rt):.1f}ms")

    # ── Recommendation ────────────────────────────────────
    print("\n🔮 Recommendation:")
    if total < 50:
        print("   ⏳ Not enough data yet. Continue collecting (need 50+ chats).")
    elif len(recent) > 20:
        print("   ✅ Good traffic. Consider retraining with new data.")
    else:
        print("   ℹ️  Traffic is low. Monitor for another week.")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    evaluate()

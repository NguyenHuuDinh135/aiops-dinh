from fastapi import FastAPI, Request
import json
import uvicorn
import os

app = FastAPI()
ALERTS_FILE = os.path.join(os.path.dirname(__file__), "alerts.jsonl")

# State
history_memory = []

@app.post("/ingest")
async def ingest(request: Request):
    payload = await request.json()
    metrics = payload.get("metrics", {})
    timestamp = payload.get("timestamp", "")

    # Extraction
    memory_usage = metrics.get("memory_usage_bytes", 0)
    requests_per_sec = metrics.get("http_requests_per_sec", 0)
    upstream_timeout_rate = metrics.get("upstream_timeout_rate", 0)
    http_5xx_rate = metrics.get("http_5xx_rate", 0)

    alerts_fired = []

    # 1. Memory Leak Detection
    history_memory.append(memory_usage)
    if len(history_memory) > 5:
        history_memory.pop(0)
    
    if memory_usage > 900_000_000:
        alerts_fired.append({
            "timestamp": timestamp,
            "type": "memory_leak",
            "severity": "critical",
            "message": f"Memory usage at {memory_usage} bytes, exceeding 900MB threshold."
        })

    # 2. Traffic Spike Detection
    if requests_per_sec > 200:
        alerts_fired.append({
            "timestamp": timestamp,
            "type": "traffic_spike",
            "severity": "critical",
            "message": f"Traffic spike detected: {requests_per_sec} req/s (normal is 80-160)."
        })
    
    # 3. Dependency Timeout Detection
    if upstream_timeout_rate > 0.8 or http_5xx_rate > 1.5:
        alerts_fired.append({
            "timestamp": timestamp,
            "type": "dependency_timeout",
            "severity": "critical",
            "message": f"High timeout rate ({upstream_timeout_rate}%) or 5xx rate ({http_5xx_rate}%)."
        })

    # Write alerts
    if alerts_fired:
        with open(ALERTS_FILE, "a") as f:
            for alert in alerts_fired:
                f.write(json.dumps(alert) + "\n")

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

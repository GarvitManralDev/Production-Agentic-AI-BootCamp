"""
Section 2.3 - Background workflows

Respond to the user first, do the slow / secondary work afterwards.

    POST /chat?message=...           -> answers instantly, logs the chat in the background
    POST /reports?topic=...          -> returns a job id immediately (202 Accepted)
    GET  /reports/{job_id}           -> poll the job: pending -> running -> completed

Run:   python 02_sync_async_background/background_demo.py
"""

import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, status

app = FastAPI(title="Background Tasks Demo")

LOG_FILE = Path(__file__).parent / "chat_logs.txt"

# Seconds a fake report takes to generate
REPORT_DELAY = 10

# In-memory job store. Production: Redis / a database + a real queue (Celery, RQ, Arq...)
jobs: dict[str, dict] = {}


# ------------------------------------------------
# Background functions
# ------------------------------------------------

def save_log(message: str, answer: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{timestamp} | user: {message} | ai: {answer}\n")


def generate_ai_report(job_id: str, topic: str) -> None:
    jobs[job_id]["status"] = "running"
    print(f"Starting AI report for: {topic}")

    # Simulate a slow LLM generating a long report
    time.sleep(REPORT_DELAY)

    jobs[job_id]["report"] = (
        f"AI GENERATED REPORT\n\nTopic: {topic}\n\n"
        f"This is the AI generated report about {topic}."
    )
    jobs[job_id]["status"] = "completed"
    print(f"Report {job_id} completed!")


# ------------------------------------------------
# Routes
# ------------------------------------------------

@app.post("/chat")
async def chat(message: str, background_tasks: BackgroundTasks):
    answer = f"AI response for: {message}"

    # Runs AFTER the response is sent - the user never waits for disk I/O
    background_tasks.add_task(save_log, message, answer)

    return {"answer": answer}


@app.post("/reports", status_code=status.HTTP_202_ACCEPTED)
async def create_report(topic: str, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:8]
    jobs[job_id] = {"job_id": job_id, "topic": topic, "status": "pending", "report": None}

    background_tasks.add_task(generate_ai_report, job_id, topic)

    # 202 = "accepted, still working on it"
    return {"job_id": job_id, "status": "pending", "poll": f"/reports/{job_id}"}


@app.get("/reports/{job_id}")
async def get_report(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )

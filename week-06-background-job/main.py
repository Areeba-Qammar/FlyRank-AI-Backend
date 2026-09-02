import logging
import datetime
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import inngest
import inngest.fast_api

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

reports: dict[str, dict] = {}

inngest_client = inngest.Inngest(
    app_id="report-api",
    logger=logging.getLogger("uvicorn"),
)

@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-a-bit", datetime.timedelta(seconds=5))
    return "Hello from the background!"


class ReportRequest(BaseModel):
    topic: Optional[str] = None


@app.post("/reports", status_code=202)
async def create_report(body: ReportRequest):
    if not body.topic or not body.topic.strip():
        raise HTTPException(status_code=400, detail="topic is required")

    report_id = str(uuid.uuid4())
    reports[report_id] = {"id": report_id, "topic": body.topic, "status": "pending"}

    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={"id": report_id, "topic": body.topic},
        )
    )

    return {"id": report_id, "status": "pending"}


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def make_report(ctx: inngest.Context) -> None:
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    def build_report() -> dict:
        if topic == "fail":
            raise Exception("The report oven is broken!")
        return {
            "id": report_id,
            "topic": topic,
            "status": "done",
            "result": f"Report about '{topic}': it's great, 10/10, would recommend.",
        }

    try:
        result = await ctx.step.run("build-report", build_report)
        reports[report_id] = result
    except Exception:
        if report_id in reports:
            reports[report_id]["status"] = "failed"
        raise


@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context) -> str:
    pending = sum(1 for r in reports.values() if r["status"] == "pending")
    done = sum(1 for r in reports.values() if r["status"] == "done")
    failed = sum(1 for r in reports.values() if r["status"] == "failed")
    summary = f"pending={pending} done={done} failed={failed}"
    ctx.logger.info(summary)
    return summary


inngest.fast_api.serve(app, inngest_client, [say_hello, make_report, heartbeat])
import sqlite3
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from report import get_report_data
from render import build_html, render_pdf

DB_PATH = "report.db"

app = FastAPI()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_reports_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_reports_table()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports", status_code=201)
def create_report():
    report_id = str(uuid.uuid4())
    os.makedirs("reports", exist_ok=True)
    file_path = f"reports/{report_id}.pdf"

    data = get_report_data()
    html = build_html(data)
    render_pdf(html, file_path)

    conn = get_db()
    conn.execute(
        "INSERT INTO reports (id, path, created_at) VALUES (?, ?, datetime('now'))",
        (report_id, file_path),
    )
    conn.commit()
    conn.close()

    return {"id": report_id, "file": f"/reports/{report_id}/file"}

@app.get("/reports/{report_id}")
def get_report(report_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file",
    }

@app.get("/reports/{report_id}/file")
def get_report_file(report_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if not row or not os.path.exists(row["path"]):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(row["path"], media_type="application/pdf", filename=f"{report_id}.pdf")
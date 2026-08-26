from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from database import get_db, init_db

app = FastAPI(title="Task Management API")

# Initialize DB on app launch
init_db()


class TaskCreate(BaseModel):
    title: str
    completed: bool = False


# Helper: To map sql on a1 contact ditionary('done' -> 'completed')
def map_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["done"]),
    }


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# STAGE 1: GET /tasks (Fetch all tasks from SQLite)
@app.get("/tasks", status_code=status.HTTP_200_OK)
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    return [map_task(row) for row in rows]


# STAGE 1: GET /tasks/{task_id} (Fetch single task from SQLite)
@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def get_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return map_task(row)
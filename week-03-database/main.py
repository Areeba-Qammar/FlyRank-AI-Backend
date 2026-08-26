from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from database import get_db, init_db

app = FastAPI()

# Initialize database on application load
init_db()


# Pydantic schema for creating a task
class TaskCreate(BaseModel):
    title: str
    completed: bool = False


# Helper function to convert DB row to API response format
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


# STAGE 1: Get all tasks
@app.get("/tasks", status_code=status.HTTP_200_OK)
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    return [map_task(row) for row in rows]


# STAGE 1: Get single task by ID
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


# STAGE 2: Create a new task
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    # Return 400 error if title is empty or only whitespace
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty",
        )

    clean_title = task.title.strip()

    # Insert new record into database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (clean_title, int(task.completed)),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": clean_title, "completed": task.completed}
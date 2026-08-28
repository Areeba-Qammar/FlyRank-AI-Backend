from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from database import get_db, init_db

app = FastAPI()

# Initialize database on application launch
init_db()


# Pydantic schema for task creation and updates
class TaskCreate(BaseModel):
    title: str
    completed: bool = False


# Helper function to map database row to API response format
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
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty",
        )

    clean_title = task.title.strip()

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


# STAGE 3: Update existing task by ID
@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_update: TaskCreate):
    if not task_update.title or not task_update.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty",
        )

    clean_title = task_update.title.strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (clean_title, int(task_update.completed), task_id),
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    conn.close()
    return {"id": task_id, "title": clean_title, "completed": task_update.completed}


# STAGE 3: Delete task by ID
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    conn.close()
    return None
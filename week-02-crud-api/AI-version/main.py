from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Task Management API")

class Task(BaseModel):
    id: int
    title: str
    completed: bool = False

class TaskCreate(BaseModel):
    title: str
    completed: bool = False

tasks_db: List[Task] = [
    Task(id=1, title="Setup development environment", completed=True),
    Task(id=2, title="Build FastAPI endpoints", completed=False)
]

@app.get("/")
def read_root():
    return {"message": "Welcome to Task API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks", response_model=List[Task])
def get_all_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task)
def get_single_task(task_id: int):
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", response_model=Task, status_code=201)
def create_new_task(task: TaskCreate):
    new_id = max([t.id for t in tasks_db], default=0) + 1
    new_task = Task(id=new_id, title=task.title, completed=task.completed)
    tasks_db.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", response_model=Task)
def update_existing_task(task_id: int, task_data: TaskCreate):
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            updated_task = Task(id=task_id, title=task_data.title, completed=task_data.completed)
            tasks_db[index] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_existing_task(task_id: int):
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            tasks_db.pop(index)
            return None
    raise HTTPException(status_code=404, detail="Task not found")
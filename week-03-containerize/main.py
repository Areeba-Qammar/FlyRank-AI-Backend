from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from sqlmodel import Session, select
from database import Task, engine, init_db


class TaskCreate(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: str
    done: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Stage 2: READ Endpoints
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


# Stage 3: CREATE, UPDATE, DELETE Endpoints
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    if not task_data.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    with Session(engine) as session:
        db_task = Task(title=task_data.title, done=task_data.done)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: TaskUpdate):
    if not task_data.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    with Session(engine) as session:
        db_task = session.get(Task, task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        db_task.title = task_data.title
        db_task.done = task_data.done
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with Session(engine) as session:
        db_task = session.get(Task, task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        session.delete(db_task)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
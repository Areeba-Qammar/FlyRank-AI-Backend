import os
from dotenv import load_dotenv
from sqlmodel import Field, SQLModel, Session, create_engine, select

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)


class Task(SQLModel, table=True):
    __tablename__ = "tasks"  # Explicit table name for checkpoint test

    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = Field(default=False)


def init_db():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.exec(select(Task)).first()
        if not existing:
            seed_tasks = [
                Task(title="Learn Docker basics", done=True),
                Task(title="Connect FastAPI to Postgres", done=False),
                Task(title="Containerize full stack", done=False),
            ]
            session.add_all(seed_tasks)
            session.commit()
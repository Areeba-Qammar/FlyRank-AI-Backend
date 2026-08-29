from fastapi import FastAPI
from src.routes.enrich import router

app = FastAPI()
app.include_router(router)
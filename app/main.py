from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.api.v1 import user
from app.api.v1 import transcription
from app.api.v1 import audio
from app.api.v1 import task
from app.ui.v1 import ui
from app.core.config import config
from app.core.logging import setup_logging
from app.db.schema import Base, engine
from app.helpers import (
    is_db_ready,
    delete_local_data,
    preload_tasks,
    un_assign_tasks
)
import logging

setup_logging()
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Checking database connection...")
    if is_db_ready():
        logging.info("Database is ready")
        preload_tasks()
    yield
    un_assign_tasks()
    delete_local_data()

app = FastAPI(title=config.app_name, lifespan=lifespan)


# Register routes
app.include_router(user.router, prefix="/api/v1")
app.include_router(ui.router)
app.include_router(transcription.router, prefix="/api/v1")
app.include_router(audio.router, prefix="/api/v1")
app.include_router(task.router, prefix="/api/v1")

# Mount static folder
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
app.mount("/data", StaticFiles(directory=config.DATA_DIR), name="data")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "ok"}


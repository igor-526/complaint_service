from fastapi import FastAPI

from logging_config import setup_logging

from routers.complaint import router as complaint_router

setup_logging()
app = FastAPI()

app.include_router(complaint_router)

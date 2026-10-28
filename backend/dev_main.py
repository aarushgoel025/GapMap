from fastapi import FastAPI
from app.jd_analytics.router import router

app = FastAPI()
app.include_router(router)
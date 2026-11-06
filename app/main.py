from fastapi import FastAPI

from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")

@app.get("/")
def home():
    return {"message": "URL shortener is running"}
@app.get("/hello")
def hello():
    return {"message": "Hello from my API"}

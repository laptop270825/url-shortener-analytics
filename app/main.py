# from fastapi import FastAPI

# from app.database import engine, Base
# from app import models

# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="URL Shortener")

# @app.get("/")
# def home():
#     return {"message": "URL shortener is running"}
# @app.get("/hello")
# def hello():
#     return {"message": "Hello from my API"}
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas
from app.utils import encode_base62

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")


@app.get("/")
def home():
    return {"message": "URL shortener is running"}


@app.post("/shorten", response_model=schemas.URLResponse)
def shorten(payload: schemas.URLCreate, db: Session = Depends(get_db)):
    link = models.Link(original_url=payload.url)
    db.add(link)
    db.flush()  # assigns the id without finishing the save
    link.short_code = encode_base62(link.id)
    db.commit()
    db.refresh(link)
    return link
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
'''Day 3'''
#from fastapi import FastAPI, Depends
#from sqlalchemy.orm import Session
'''Day 4'''
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse

from app.database import engine, Base, get_db
from app import models, schemas
from app.utils import encode_base62

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")


@app.get("/")
def home():
    return {"message": "URL shortener is running"}


'''@app.post("/shorten", response_model=schemas.URLResponse)
def shorten(payload: schemas.URLCreate, db: Session = Depends(get_db)):
    link = models.Link(original_url=payload.url)
    db.add(link) # adds the link to the database
    db.flush()  # assigns the id without finishing the save
    link.short_code = encode_base62(link.id)
    db.commit()  # commits the transaction
    db.refresh(link) # refreshes the instance with the latest data from the database
    return link'''
@app.post("/shorten", response_model=schemas.URLResponse)
def shorten(payload: schemas.URLCreate, db: Session = Depends(get_db)):
    url = str(payload.url)

    existing = (
        db.query(models.Link)
        .filter(models.Link.original_url == url)
        .first()
    )
    if existing:
        return existing

    link = models.Link(original_url=url)
    db.add(link)
    db.flush()
    link.short_code = encode_base62(link.id)
    db.commit()
    db.refresh(link)
    return link
@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    link = (
        db.query(models.Link)
        .filter(models.Link.short_code == short_code)
        .first()
    )
    if link is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    return RedirectResponse(url=link.original_url)
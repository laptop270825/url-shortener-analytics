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

from fastapi import FastAPI, Depends, HTTPException, Request
#from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas
from app.utils import encode_base62, detect_device

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from collections import Counter
from pathlib import Path

from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy import func

from fastapi.responses import FileResponse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

Base.metadata.create_all(bind=engine)

#app = FastAPI(title="URL Shortener")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="URL Shortener")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


'''@app.post("/shorten", response_model=schemas.URLResponse)
def shorten(payload: schemas.URLCreate, db: Session = Depends(get_db)):
    link = models.Link(original_url=payload.url)
    db.add(link) # adds the link to the database
    db.flush()  # assigns the id without finishing the save
    link.short_code = encode_base62(link.id)
    db.commit()  # commits the transaction
    db.refresh(link) # refreshes the instance with the latest data from the database
    return link'''
#@app.post("/shorten", response_model=schemas.URLResponse)
#def shorten(payload: schemas.URLCreate, db: Session = Depends(get_db)):
@app.post("/shorten", response_model=schemas.URLResponse)
@limiter.limit("10/minute")
def shorten(request: Request, payload: schemas.URLCreate, db: Session = Depends(get_db)):
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

@app.get("/stats/{short_code}", response_model=schemas.StatsResponse)
def stats(short_code: str, db: Session = Depends(get_db)):
    link = (
        db.query(models.Link)
        .filter(models.Link.short_code == short_code)
        .first()
    )
    if link is None:
        raise HTTPException(status_code=404, detail="Short link not found")

    recent = (
        db.query(models.Click)
        .filter(models.Click.link_id == link.id)
        .order_by(models.Click.clicked_at.desc())
        .limit(10)
        .all()
    )

    return {
        "short_code": link.short_code,
        "original_url": link.original_url,
        "click_count": link.click_count,
        "created_at": link.created_at,
        "recent_clicks": recent,
    }

'''@app.get("/api/analytics")
def analytics(db: Session = Depends(get_db)):
    clicks = db.query(models.Click).all()
    per_day = Counter(c.clicked_at.date().isoformat() for c in clicks)
    devices = Counter(detect_device(c.user_agent) for c in clicks)
    top_links = (
        db.query(models.Link)
        .order_by(models.Link.click_count.desc())
        .limit(5)
        .all()
    )
    return {
        "total_links": db.query(func.count(models.Link.id)).scalar(),
        "total_clicks": len(clicks),
        "clicks_per_day": dict(sorted(per_day.items())),
        "devices": dict(devices),
        "top_links": [
            {"short_code": l.short_code, "url": l.original_url, "clicks": l.click_count}
            for l in top_links
        ],
    }'''

@app.get("/api/analytics")
def analytics(db: Session = Depends(get_db)):
    day = func.date(models.Click.clicked_at)
    per_day_rows = (
        db.query(day, func.count(models.Click.id))
        .group_by(day)
        .order_by(day)
        .all()
    )

    ua_rows = (
        db.query(models.Click.user_agent, func.count(models.Click.id))
        .group_by(models.Click.user_agent)
        .all()
    )
    devices = Counter()
    for user_agent, n in ua_rows:
        devices[detect_device(user_agent)] += n

    top_links = (
        db.query(models.Link)
        .order_by(models.Link.click_count.desc())
        .limit(5)
        .all()
    )

    return {
        "total_links": db.query(func.count(models.Link.id)).scalar(),
        "total_clicks": db.query(func.count(models.Click.id)).scalar(),
        "clicks_per_day": {str(d): n for d, n in per_day_rows},
        "devices": dict(devices),
        "top_links": [
            {"short_code": l.short_code, "url": l.original_url, "clicks": l.click_count}
            for l in top_links
        ],
    }

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    page = Path(__file__).parent / "static" / "dashboard.html"
    return page.read_text(encoding="utf-8")

@app.get("/{short_code}")
def redirect(short_code: str, request: Request, db: Session = Depends(get_db)):
    link = (
        db.query(models.Link)
        .filter(models.Link.short_code == short_code)
        .first()
    )
    if link is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    click = models.Click(
        link_id=link.id,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )
    '''db.add(click)
    link.click_count += 1
    db.commit()'''
    target = link.original_url
    db.add(click)
    db.query(models.Link).filter(models.Link.id == link.id).update(
        {models.Link.click_count: models.Link.click_count + 1}
    )
    db.commit()

    return RedirectResponse(url=target)
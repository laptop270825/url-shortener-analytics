import random
from datetime import datetime, timedelta

from app.database import SessionLocal, engine, Base
from app import models
from app.utils import encode_base62

Base.metadata.create_all(bind=engine)
db = SessionLocal()

sites = [
    "https://www.google.com/",
    "https://github.com/",
    "https://www.wikipedia.org/",
    "https://stackoverflow.com/",
    "https://www.python.org/",
]
agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) Mobile Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14) Chrome/120.0 Mobile",
    "Mozilla/5.0 (iPad; CPU OS 17_0) Safari/604.1",
]
referrers = [None, "https://twitter.com/", "https://www.linkedin.com/", "https://t.me/"]

now = datetime.datetime.utcnow()
for url in sites:
    link = db.query(models.Link).filter(models.Link.original_url == url).first()
    if link is None:
        link = models.Link(original_url=url)
        db.add(link)
        db.flush()
        link.short_code = encode_base62(link.id)
    n = random.randint(10, 60)
    for _ in range(n):
        db.add(models.Click(
            link_id=link.id,
            clicked_at=now - timedelta(days=random.randint(0, 13), hours=random.randint(0, 23)),
            user_agent=random.choice(agents),
            referrer=random.choice(referrers),
        ))
    link.click_count += n

db.commit()
print("Demo data added.")
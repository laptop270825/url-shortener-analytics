from fastapi import FastAPI

app = FastAPI(title="URL Shortener")

@app.get("/")
def home():
    return {"message": "URL shortener is running"}
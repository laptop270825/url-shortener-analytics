from fastapi import FastAPI

app = FastAPI(title="URL Shortener")

@app.get("/")
def home():
    return {"message": "URL shortener is running"}
@app.get("/hello")
def hello():
    return {"Hello from my API"}

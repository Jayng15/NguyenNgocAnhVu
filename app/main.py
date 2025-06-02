# Entry point for FastAPI app
from fastapi import FastAPI

from app.routes import user, message

app = FastAPI()

app.include_router(user.router)
app.include_router(message.router)


@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

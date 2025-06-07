# Entry point for FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app
from app.routes import message, user

app = FastAPI(
    title="Messaging API", description="simple API for messaging", version="1.0.0"
)

# add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(message.router)


@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

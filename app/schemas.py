# Pydantic models
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: str = Field(..., description="User's unique email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's name")

    class Config:
        orm_mode = True

class UserPublic(BaseModel):
    id: UUID
    email: str = Field(..., description="User's unique email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's name")
    created_at: datetime = Field(..., description="Timestamp when the user was created")

    class Config:
        orm_mode = True

class Message(BaseModel):
    id: UUID
    sender_id: UUID
    subject: Optional[str] = Field(None, max_length=255, description="Message subject")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime

    class Config:
        orm_mode = True

class MessageRecipient(BaseModel):
    id: UUID
    message_id: UUID
    recipient_id: UUID
    read: bool = Field(False, description="Read status")
    read_at: Optional[datetime] = Field(None, description="Timestamp when message was read")

    class Config:
        orm_mode = True

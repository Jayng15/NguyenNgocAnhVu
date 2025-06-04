# Pydantic models
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: str = Field(..., description="User's unique email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's name")

    @field_validator('email')
    def validate_email(cls, value: str) -> str:
        """
        Validate that the email has a basic correct format.
        Converts the email to lowercase and strips whitespace.
        """
        value = value.strip().lower()
        if '@' not in value or '.' not in value.split('@')[-1]:
            raise ValidationError("Invalid email format")
        if value.count('@') != 1:
            raise ValidationError("Email must contain exactly one '@' symbol")
        local, domain = value.split('@')
        if not local or not domain or '.' not in domain:
            raise ValidationError("Invalid email format")
        return value

    class ConfigDict:
        orm_mode = True

class UserPublic(BaseModel):
    id: UUID
    email: str = Field(..., description="User's unique email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's name")
    created_at: datetime = Field(..., description="Timestamp when the user was created")

    class ConfigDict:
        orm_mode = True

class MessageCreate(BaseModel):
    sender_email: str = Field(..., description="Sender's email address")
    recipient_emails: list[str] = Field(..., description="List of recipient emails")
    subject: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1)

    @field_validator('sender_email')
    def validate_sender_email(cls, value: str) -> str:
        """
        Validate that the sender's email has a basic correct format.
        Converts the email to lowercase and strips whitespace.
        """
        value = value.strip().lower()
        if '@' not in value or '.' not in value.split('@')[-1]:
            raise ValidationError("Invalid sender email format")
        if value.count('@') != 1:
            raise ValidationError("Sender email must contain exactly one '@' symbol")
        local, domain = value.split('@')
        if not local or not domain or '.' not in domain:
            raise ValidationError("Invalid sender email format")
        return value
    
    @field_validator('recipient_emails')
    def validate_recipient_emails(cls, value: list[str]) -> list[str]:
        """
        Validate that all recipient emails have a basic correct format.
        Converts the emails to lowercase and strips whitespace.
        """
        if not value:
            raise ValidationError("At least one recipient email is required")
        
        for email in value:
            email = email.strip().lower()
            if '@' not in email or '.' not in email.split('@')[-1]:
                raise ValidationError(f"Invalid recipient email format: {email}")
            if email.count('@') != 1:
                raise ValidationError(f"Recipient email must contain exactly one '@' symbol: {email}")
            local, domain = email.split('@')
            if not local or not domain or '.' not in domain:
                raise ValidationError(f"Invalid recipient email format: {email}")
        
        return value
    
    class ConfigDict:
        orm_mode = True
    
class SentMessage(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the message")
    sender_email: str = Field(..., description="Sender's email address", max_length=254)
    recipient_emails: list[str] = Field(
        ..., 
        description="List of recipient email addresses", 
        min_length=1, 
        max_length=50
    )
    subject: Optional[str] = Field(None, description="Message subject", max_length=255)
    content: str = Field(..., description="Message content", min_length=1, max_length=5000)
    timestamp: datetime = Field(..., description="Time when the message was sent")

    class ConfigDict:
        orm_mode = True

class InboxMessage(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the message")
    sender_email: str = Field(..., description="Sender's email address", max_length=254)
    subject: Optional[str] = Field(None, description="Message subject", max_length=255)
    content: str = Field(..., description="Message content", min_length=1, max_length=5000)
    timestamp: datetime = Field(..., description="Time when the message was received")
    read: bool = Field(False, description="Read status of the message")
    read_at: Optional[datetime] = Field(None, description="Timestamp when the message was read")

    class ConfigDict:
        orm_mode = True
        
class MessageRecipientInfo(BaseModel):
    email: str = Field(..., description="Recipient's email address", max_length=254)
    read: bool = Field(False, description="Read status for this recipient")
    read_at: Optional[datetime] = Field(None, description="Timestamp when this recipient read the message")

    class ConfigDict:
        orm_mode = True

class MessageDetail(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the message")
    sender_email: str = Field(..., description="Sender's email address", max_length=254)
    subject: Optional[str] = Field(None, description="Message subject", max_length=255)
    content: str = Field(..., description="Message content", min_length=1, max_length=5000)
    timestamp: datetime = Field(..., description="Time when the message was sent")
    recipients: list[MessageRecipientInfo] = Field(
        default_factory=list, 
        description="List of recipients with read status"
    )

    class ConfigDict:
        orm_mode = True

# SQLAlchemy models using Mapped and mapped_column
from sqlalchemy import String, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime

from app.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sent_messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="sender",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    received_messages: Mapped[list["MessageRecipient"]] = relationship(
        "MessageRecipient",
        back_populates="recipient",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    subject: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sender: Mapped["User"] = relationship("User", back_populates="sent_messages")
    recipients: Mapped[list["MessageRecipient"]] = relationship(
        "MessageRecipient", back_populates="message", cascade="all, delete-orphan", passive_deletes=True
    )

class MessageRecipient(Base):
    __tablename__ = "message_recipients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="recipients")
    recipient: Mapped["User"] = relationship("User", back_populates="received_messages")


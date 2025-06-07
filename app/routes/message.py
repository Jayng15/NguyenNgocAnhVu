from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import app
from app.db import get_db
from app.repositories.message_repository import MessageRepository
from app.schemas import (InboxMessage, MessageCreate, MessageDetail,
                         MessageRecipientInfo, SentMessage)


def get_message_repository(db: Session = Depends(get_db)) -> MessageRepository:
    return MessageRepository(db)


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post(
    "/",
    summary="Send a message",
    status_code=status.HTTP_201_CREATED,
    operation_id="send_message",
    response_model=SentMessage,
)
def send_message(
    message: MessageCreate, repo: MessageRepository = Depends(get_message_repository)
) -> SentMessage:
    """Send a message to one or more recipients.

    Args:
        message (MessageCreate): The message data to send.
        repo (MessageRepository): The message repository dependency.

    Returns:
        SentMessage: The sent message details.

    Raises:
        HTTPException: If the sender does not exist or if a recipient does not exist.

    """
    try:
        sent_message = repo.send_message(message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return sent_message


@router.get(
    "/sent/{sender_email}",
    summary="Get sent messages",
    status_code=status.HTTP_200_OK,
    operation_id="get_sent_messages",
    response_model=list[SentMessage],
)
def get_sent_messages(
    sender_email: str, repo: MessageRepository = Depends(get_message_repository)
) -> list[SentMessage]:
    """Retrieve all sent messages for a given sender.

    Args:
        sender_email (str): The email of the sender.
        repo (MessageRepository): The message repository dependency.

    Returns:
        list[SentMessage]: A list of sent messages.

    Raises:
        HTTPException: If the sender does not exist.

    """
    try:
        return repo.get_sent_messages(sender_email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/inbox/{recipient_email}",
    summary="Get inbox messages",
    status_code=status.HTTP_200_OK,
    operation_id="get_inbox_messages",
    response_model=list[InboxMessage],
)
def get_inbox_messages(
    recipient_email: str, repo: MessageRepository = Depends(get_message_repository)
) -> list[InboxMessage]:
    """Retrieve all inbox messages for a given recipient.

    Args:
        recipient_email (str): The email of the recipient.
        repo (MessageRepository): The message repository dependency.

    Returns:
        list[InboxMessage]: A list of inbox messages.

    Raises:
        HTTPException: If the recipient does not exist.

    """
    try:
        return repo.get_inbox_messages(recipient_email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{message_id}",
    summary="Get message details",
    status_code=status.HTTP_200_OK,
    operation_id="get_message_detail",
    response_model=MessageDetail,
)
def get_message_detail(
    message_id: UUID, repo: MessageRepository = Depends(get_message_repository)
) -> MessageDetail:
    """Retrieve detailed information about a specific message.

    Args:
        message_id (str): The unique identifier of the message.
        repo (MessageRepository): The message repository dependency.

    Returns:
        MessageDetail: Detailed information about the message.

    Raises:
        HTTPException: If the message does not exist.

    """
    try:
        return repo.get_message_detail(message_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/unread/{recipient_email}",
    summary="Get unread messages",
    status_code=status.HTTP_200_OK,
    operation_id="get_unread_messages",
    response_model=list[InboxMessage],
)
def get_unread_messages(
    recipient_email: str, repo: MessageRepository = Depends(get_message_repository)
) -> list[InboxMessage]:
    """Retrieve all unread messages in the inbox for a given recipient.

    Args:
        recipient_email (str): The email of the recipient.
        repo (MessageRepository): The message repository dependency.

    Returns:
        list[InboxMessage]: A list of unread inbox messages.

    Raises:
        HTTPException: If the recipient does not exist.

    """
    try:
        return repo.get_unread_messages(recipient_email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/read/{message_id}",
    summary="Mark message as read",
    status_code=status.HTTP_200_OK,
    operation_id="mark_message_as_read",
)
def mark_message_as_read(
    message_id: UUID,
    recipient_email: str = Query(
        ..., description="Email of the recipient marking the message as read"
    ),
    repo: MessageRepository = Depends(get_message_repository),
):
    """Mark a specific message as read.

    Args:
        message_id (str): The unique identifier of the message.
        recipient_email (str): The email of the recipient marking the message as read.
        repo (MessageRepository): The message repository dependency.

    Returns:
        dict: Success message confirming the message was marked as read.

    Raises:
        HTTPException: If the message does not exist or if it is already read.

    """
    try:
        repo.mark_message_as_read(message_id, recipient_email)
        return {"detail": "Message marked as read successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

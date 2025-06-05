from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas import MessageCreate, SentMessage, InboxMessage, MessageRecipientInfo, MessageDetail
from app.db import get_db
from app.repositories.message_repository import MessageRepository

def get_message_repository(db: Session = Depends(get_db)) -> MessageRepository:
    return MessageRepository(db)    

router = APIRouter(
    prefix='/messages',
    tags=['Messages']
)

@router.post(
    '/',
    summary="Send a message",
    status_code=status.HTTP_201_CREATED,
    response_model=SentMessage
)
async def send_message(
    message: MessageCreate,
    repo: MessageRepository = Depends(get_message_repository)) -> SentMessage:
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
        sent_message = await repo.send_message(message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return sent_message

@router.get(
    '/sent/{sender_email}',
    summary="Get sent messages",
    status_code=status.HTTP_200_OK,
    response_model=list[SentMessage]
)
async def get_sent_messages(
    sender_email: str,
    repo: MessageRepository = Depends(get_message_repository)
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
        return await repo.get_sent_messages(sender_email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get(
    '/inbox/{recipient_email}',
    summary="Get inbox messages",
    status_code=status.HTTP_200_OK,
    response_model=list[InboxMessage]
)
async def get_inbox_messages(
    recipient_email: str,
    repo: MessageRepository = Depends(get_message_repository)
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
        return await repo.get_inbox_messages(recipient_email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get(
    '/{message_id}',
    summary="Get message details",
    status_code=status.HTTP_200_OK,
    response_model=MessageDetail
)
async def get_message_detail(
    message_id: UUID,
    repo: MessageRepository = Depends(get_message_repository)
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
        return await repo.get_message_detail(message_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get(
    '/unread/{recipient_email}',
    summary="Get unread messages",
    status_code=status.HTTP_200_OK,
    response_model=list[InboxMessage]
)
async def get_unread_messages(
    recipient_email: str,
    repo: MessageRepository = Depends(get_message_repository)
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
        return await repo.get_unread_messages(recipient_email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.patch(
    '/read/{message_id}',
    summary="Mark message as read",
    status_code=status.HTTP_200_OK,
)
async def mark_message_as_read(
    message_id: UUID,
    recipient_email: str = Query(..., description="Email of the recipient marking the message as read"),
    repo: MessageRepository = Depends(get_message_repository)
):
    """Mark a specific message as read.

    Args:
        message_id (str): The unique identifier of the message.
        recipient_email (str): The email of the recipient marking the message as read.
        repo (MessageRepository): The message repository dependency.
        
    Returns:
        MessageDetail: Updated information about the message.

    Raises:
        HTTPException: If the message does not exist or if it is already read.

    """
    try:
        await repo.mark_message_as_read(message_id, recipient_email)
        return {"detail": "Message marked as read successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
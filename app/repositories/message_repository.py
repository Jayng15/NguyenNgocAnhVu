from sqlalchemy.orm import Session
from app.models import User, Message, MessageRecipient
from app.schemas import MessageCreate, SentMessage, InboxMessage, MessageRecipientInfo, MessageDetail
from datetime import datetime

class MessageRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def send_message(self, message_data: MessageCreate) -> SentMessage:
        """
        Send a message to one or more recipients.
        
        Args:
            message_data (MessageCreate): The message data to send.
        
        Returns:
            SentMessage: The sent message details.
        """
        sender = self.db_session.query(User).filter(User.email == message_data.sender_email).first()
        if not sender:
            raise ValueError("Sender does not exist.")
        
        new_message = Message(
            sender_id=sender.id,
            subject=message_data.subject,
            content=message_data.content
        )
        
        self.db_session.add(new_message)
        self.db_session.commit()
        self.db_session.refresh(new_message)
        
        for recipient_email in message_data.recipient_emails:
            recipient = self.db_session.query(User).filter(User.email == recipient_email).first()
            if not recipient:
                raise ValueError(f"Recipient {recipient_email} does not exist.")
            
            new_recipient = MessageRecipient(
                message_id=new_message.id,
                recipient_id=recipient.id
            )
            self.db_session.add(new_recipient)
        
        self.db_session.commit()
        
        return SentMessage(
            id=new_message.id,
            sender_email=sender.email,
            recipient_emails=message_data.recipient_emails,
            subject=message_data.subject,
            content=message_data.content,
            timestamp=new_message.timestamp
        )
    
    async def get_sent_messages(self, sender_email: str) -> list[SentMessage]:
        """
        Retrieve all sent messages for a given sender.
        
        Args:
            sender_email (str): The email of the sender.
        
        Returns:
            list[SentMessage]: List of sent messages.
        """
        sender = self.db_session.query(User).filter(User.email == sender_email).first()
        if not sender:
            raise ValueError("Sender does not exist.")
        
        messages = self.db_session.query(Message).filter(Message.sender_id == sender.id).all()
        
        return [
            SentMessage(
                id=message.id,
                sender_email=sender_email,
                recipient_emails=[recipient.recipient.email for recipient in message.recipients],
                subject=message.subject,
                content=message.content,
                timestamp=message.timestamp
            ) for message in messages
        ]

    async def get_inbox_messages(self, recipient_email: str) -> list[InboxMessage]:
        """
        Retrieve all messages in the inbox for a given recipient.
        
        Args:
            recipient_email (str): The email of the recipient.
        Returns:
            list[InboxMessage]: List of inbox messages.
        """
        recipient = self.db_session.query(User).filter(User.email == recipient_email).first()
        if not recipient:
            raise ValueError("Recipient does not exist.")
        
        message_recipients = self.db_session.query(MessageRecipient).filter(
            MessageRecipient.recipient_id == recipient.id).all()
        messages = []
        for message_recipient in message_recipients:
            message = message_recipient.message
            messages.append(
                InboxMessage(
                    id=message.id,
                    sender_email=message.sender.email,
                    subject=message.subject,
                    content=message.content,
                    timestamp=message.timestamp,
                    read=message_recipient.read,
                    read_at=message_recipient.read_at
                )
            )
        return messages

    async def get_unread_messages(self, recipient_email: str) -> list[InboxMessage]:
        """
        Retrieve all unread messages in the inbox for a given recipient.
        
        Args:
            recipient_email (str): The email of the recipient.
        
        Returns:
            list[InboxMessage]: List of unread inbox messages.
        """
        recipient = self.db_session.query(User).filter(User.email == recipient_email).first()
        if not recipient:
            raise ValueError("Recipient does not exist.")
        
        message_recipients = self.db_session.query(MessageRecipient).filter(
            MessageRecipient.recipient_id == recipient.id,
            MessageRecipient.read == False
        ).all()
        
        messages = []
        for message_recipient in message_recipients:
            message = message_recipient.message
            messages.append(
                InboxMessage(
                    id=message.id,
                    sender_email=message.sender.email,
                    subject=message.subject,
                    content=message.content,
                    timestamp=message.timestamp,
                    read=message_recipient.read,
                    read_at=message_recipient.read_at
                )
            )
        return messages

    async def get_message_detail(self, message_id: str) -> MessageDetail:
        """
        Retrieve recipients about a specific message.
        
        Args:
            message_id (str): The ID of the message to retrieve.
        
        Returns:
            MessageDetail: Detailed information about the message.
        """
        message = self.db_session.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise ValueError("Message does not exist.")
        
        recipients_info = [
            MessageRecipientInfo(
                email=recipient.recipient.email,
                read=recipient.read,
                read_at=recipient.read_at
            ) for recipient in message.recipients
        ]
        
        return MessageDetail(
            id=message.id,
            sender_email=message.sender.email,
            subject=message.subject,
            content=message.content,
            timestamp=message.timestamp,
            recipients=recipients_info
        )

    async def mark_message_as_read(self, message_id: str, recipient_email: str) -> None:
        """
        Mark a message as read for a specific recipient.
        Args:
            message_id (str): The ID of the message to mark as read.
            recipient_email (str): The email of the recipient marking the message as read.
        Raises:
            ValueError: If the message or recipient does not exist.
        """
        recipient = self.db_session.query(User).filter(User.email == recipient_email).first()
        if not recipient:
            raise ValueError("Recipient does not exist.")
        
        message_recipient = self.db_session.query(MessageRecipient).filter(
            MessageRecipient.message_id == message_id,
            MessageRecipient.recipient_id == recipient.id
        ).first()

        if not message_recipient:
            raise ValueError("Message does not exist for this recipient.")

        if message_recipient.read:
            raise ValueError("Message has already been marked as read.")
        
        message_recipient.read = True
        message_recipient.read_at = datetime.utcnow()
        
        self.db_session.commit()
        
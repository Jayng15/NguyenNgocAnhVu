import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastmcp import FastMCP

import app
from app.db import get_db
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.schemas import MessageCreate, UserCreate, UserPublic


def get_user_repository():
    db = next(get_db())
    return UserRepository(db)


def get_message_repository():
    db = next(get_db())
    return MessageRepository(db)


mcp = FastMCP("Messaging API")


@mcp.tool()
def create_user(name: str, email: str) -> str:
    """
    Create a new user with the given name and email.
    """
    try:
        repo = get_user_repository()
        user_data = UserCreate(name=name, email=email)
        user = repo.create_user(user_data)
        return f"User '{user.name}' with email '{user.email}' created successfully. ID: {user.id}"
    except ValueError as e:
        return f"Error creating user: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_users(user_id: Optional[str] = None) -> str:
    """
    Get all users or a specific user by ID.
    """
    try:
        repo = get_user_repository()

        if user_id:
            # Get specific user by ID
            user_uuid = UUID(user_id)
            user = repo.get_user_by_id(user_uuid)

            if not user:
                return "User not found"

            user_data = {"id": str(user.id), "name": user.name, "email": user.email}

            return json.dumps(user_data, indent=2)
        else:
            # Get all users
            users = repo.get_users()

            users_data = []
            for user in users:
                users_data.append(
                    {"id": str(user.id), "name": user.name, "email": user.email}
                )

            return json.dumps(users_data, indent=2)

    except ValueError as e:
        return f"Error retrieving users: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def send_message(
    sender_email: str,
    recipient_emails: List[str],
    content: str,
    subject: Optional[str] = None,
) -> str:
    """
    Send a message to one or more recipients using email addresses.
    """
    try:
        repo = get_message_repository()
        message_data = MessageCreate(
            sender_email=sender_email,
            recipient_emails=recipient_emails,
            content=content,
            subject=subject,
        )
        sent_message = repo.send_message(message_data)

        recipients_str = ", ".join(recipient_emails)
        return f"Message sent successfully to {recipients_str}. Message ID: {sent_message.id}"
    except ValueError as e:
        return f"Error sending message: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_messages(user_email: str) -> str:
    """
    Get all messages for a user (both sent and received) using email address.
    """
    try:
        repo = get_message_repository()

        sent_messages = repo.get_sent_messages(user_email)

        inbox_messages = repo.get_inbox_messages(user_email)

        all_messages = []

        for msg in sent_messages:
            all_messages.append(
                {
                    "id": str(msg.id),
                    "type": "sent",
                    "subject": msg.subject,
                    "content": msg.content,
                    "recipient_emails": msg.recipient_emails,
                    "timestamp": str(msg.timestamp),
                }
            )

        for msg in inbox_messages:
            all_messages.append(
                {
                    "id": str(msg.id),
                    "type": "received",
                    "subject": msg.subject,
                    "content": msg.content,
                    "sender_email": msg.sender_email,
                    "timestamp": str(msg.timestamp),
                    "read": msg.read,
                    "read_at": str(msg.read_at) if msg.read_at else None,
                }
            )

        all_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return json.dumps(all_messages, indent=2)
    except ValueError as e:
        return f"Error retrieving messages: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def mark_message_read(message_id: str, recipient_email: str) -> str:
    """
    Mark a message as read using message ID and recipient email.
    """
    try:
        repo = get_message_repository()
        repo.mark_message_as_read(message_id, recipient_email)
        return f"Message {message_id} marked as read successfully"
    except ValueError as e:
        return f"Error marking message as read: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_unread_messages(recipient_email: str) -> str:
    """
    Get all unread messages for a user using email address.
    """
    try:
        repo = get_message_repository()
        unread_messages = repo.get_unread_messages(recipient_email)

        messages_data = []
        for msg in unread_messages:
            messages_data.append(
                {
                    "id": str(msg.id),
                    "subject": msg.subject,
                    "content": msg.content,
                    "sender_email": msg.sender_email,
                    "timestamp": str(msg.timestamp),
                    "read": msg.read,
                    "read_at": str(msg.read_at) if msg.read_at else None,
                }
            )

        return json.dumps(messages_data, indent=2)
    except ValueError as e:
        return f"Error retrieving unread messages: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_sent_messages(sender_email: str) -> str:
    """
    Get all messages sent by a user using email address.
    """
    try:
        repo = get_message_repository()
        sent_messages = repo.get_sent_messages(sender_email)

        messages_data = []
        for msg in sent_messages:
            messages_data.append(
                {
                    "id": str(msg.id),
                    "subject": msg.subject,
                    "content": msg.content,
                    "recipient_emails": msg.recipient_emails,
                    "timestamp": str(msg.timestamp),
                }
            )

        return json.dumps(messages_data, indent=2)
    except ValueError as e:
        return f"Error retrieving sent messages: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_inbox_messages(recipient_email: str) -> str:
    """
    Get all messages received by a user using email address.
    """
    try:
        repo = get_message_repository()
        inbox_messages = repo.get_inbox_messages(recipient_email)

        messages_data = []
        for msg in inbox_messages:
            messages_data.append(
                {
                    "id": str(msg.id),
                    "subject": msg.subject,
                    "content": msg.content,
                    "sender_email": msg.sender_email,
                    "timestamp": str(msg.timestamp),
                    "read": msg.read,
                    "read_at": str(msg.read_at) if msg.read_at else None,
                }
            )

        return json.dumps(messages_data, indent=2)
    except ValueError as e:
        return f"Error retrieving inbox messages: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_message_detail(message_id: str) -> str:
    """
    Get detailed information about a specific message using message ID.
    """
    try:
        repo = get_message_repository()
        message_detail = repo.get_message_detail(message_id)

        detail_data = {
            "id": str(message_detail.id),
            "subject": message_detail.subject,
            "content": message_detail.content,
            "sender_email": message_detail.sender_email,
            "timestamp": str(message_detail.timestamp),
            "recipients": [
                {
                    "email": r.email,
                    "read": r.read,
                    "read_at": str(r.read_at) if r.read_at else None,
                }
                for r in message_detail.recipients
            ],
        }

        return json.dumps(detail_data, indent=2)
    except ValueError as e:
        return f"Error retrieving message detail: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.resource("users://all")
def get_all_users_resource() -> str:
    """Resource containing all users in the system."""
    return get_users()


@mcp.resource("user://{user_id}")
def get_user_resource(user_id: str) -> str:
    """Resource containing a specific user's information."""
    user_data = get_users(user_id)

    if "User not found" in user_data:
        return user_data

    try:
        user_json = json.loads(user_data)

        sent_count = len(json.loads(get_sent_messages(user_json["email"])))
        inbox_count = len(json.loads(get_inbox_messages(user_json["email"])))
        unread_count = len(json.loads(get_unread_messages(user_json["email"])))

        user_json["profile"] = {
            "messages_sent": sent_count,
            "messages_received": inbox_count,
            "unread_count": unread_count,
        }

        return json.dumps(user_json, indent=2)
    except:
        return user_data


@mcp.resource("messages://all")
def get_all_messages_resource() -> str:
    """Resource containing all messages in the system."""
    try:
        users_data = json.loads(get_users())
        all_messages = []

        for user in users_data:
            user_messages = json.loads(get_messages(user["email"]))
            all_messages.extend(user_messages)

        all_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return json.dumps(all_messages, indent=2)
    except Exception as e:
        return f"Error loading messages resource: {str(e)}"


@mcp.resource("inbox://{user_email}")
def get_user_inbox_resource(user_email: str) -> str:
    return get_inbox_messages(user_email)


@mcp.resource("outbox://{user_email}")
def get_user_outbox_resource(user_email: str) -> str:
    return get_sent_messages(user_email)


@mcp.resource("unread://{user_email}")
def get_user_unread_resource(user_email: str) -> str:
    return get_unread_messages(user_email)


@mcp.resource("message://{message_id}")
def get_message_resource(message_id: str) -> str:
    """Resource containing detailed information about a specific message."""
    message_data = get_message_detail(message_id)

    try:
        message_json = json.loads(message_data)

        recipients = message_json.get("recipients", [])
        message_json["metadata"] = {
            "total_recipients": len(recipients),
            "read_count": sum(1 for r in recipients if r.get("read", False)),
            "unread_count": sum(1 for r in recipients if not r.get("read", False)),
        }

        return json.dumps(message_json, indent=2)
    except:
        return message_data


@mcp.resource("stats://system")
def get_system_stats_resource() -> str:
    """Resource containing system-wide statistics."""
    try:
        users_data = json.loads(get_users())
        total_users = len(users_data)

        total_messages = 0
        total_unread = 0

        for user in users_data:
            sent_count = len(json.loads(get_sent_messages(user["email"])))
            unread_count = len(json.loads(get_unread_messages(user["email"])))
            total_messages += sent_count
            total_unread += unread_count

        stats_data = {
            "system_statistics": {
                "total_users": total_users,
                "total_messages": total_messages,
                "total_unread_messages": total_unread,
                "average_messages_per_user": (
                    round(total_messages / total_users, 2) if total_users > 0 else 0
                ),
                "last_updated": str(datetime.now()),
            }
        }

        return json.dumps(stats_data, indent=2)
    except Exception as e:
        return f"Error loading system stats resource: {str(e)}"


if __name__ == "__main__":
    mcp.run()

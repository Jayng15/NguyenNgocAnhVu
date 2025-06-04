import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def users():
    sender = {"email": "sender@example.com", "name": "Sender"}
    recipient = {"email": "recipient@example.com", "name": "Recipient"}
    client.post("/users/", json=sender)
    client.post("/users/", json=recipient)
    return sender, recipient

def test_send_message(users):
    sender, recipient = users
    payload = {
        "sender_email": sender["email"],
        "recipient_emails": [recipient["email"]],
        "subject": "Test Subject",
        "content": "Hello, this is a test message."
    }
    response = client.post("/messages/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["sender_email"] == sender["email"]
    assert recipient["email"] in data["recipient_emails"]
    assert data["subject"] == "Test Subject"
    assert data["content"] == "Hello, this is a test message."
    assert "id" in data

def test_get_inbox(users):
    sender, recipient = users
    payload = {
        "sender_email": sender["email"],
        "recipient_emails": [recipient["email"]],
        "subject": "Inbox Subject",
        "content": "Inbox message content."
    }
    client.post("/messages/", json=payload)

    response = client.get(f"/messages/inbox/{recipient['email']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(msg["subject"] == "Inbox Subject" for msg in data)

def test_get_sent(users):
    sender, recipient = users
    payload = {
        "sender_email": sender["email"],
        "recipient_emails": [recipient["email"]],
        "subject": "Sent Subject",
        "content": "Sent message content."
    }
    client.post("/messages/", json=payload)

    response = client.get(f"/messages/sent/{sender['email']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(msg["subject"] == "Sent Subject" for msg in data)

def test_mark_message_as_read(users):
    sender, recipient = users
    payload = {
        "sender_email": sender["email"],
        "recipient_emails": [recipient["email"]],
        "subject": "Read Test",
        "content": "Mark as read test message."
    }
    send_resp = client.post("/messages/", json=payload)
    assert send_resp.status_code == 201
    message_id = send_resp.json()["id"]

    patch_resp = client.patch(
        f"/messages/read/{message_id}",
        params={"recipient_email": recipient["email"]}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["detail"] == "Message marked as read successfully"

    # Check that the message is now marked as read in inbox
    inbox_resp = client.get(f"/messages/inbox/{recipient['email']}")
    assert inbox_resp.status_code == 200
    inbox = inbox_resp.json()
    msg = next((m for m in inbox if m["id"] == message_id), None)
    assert msg is not None
    assert msg["read"] is True

def test_get_unread_messages(users):
    sender, recipient = users
    payload = {
        "sender_email": sender["email"],
        "recipient_emails": [recipient["email"]],
        "subject": "Unread Test",
        "content": "Unread message content."
    }
    send_resp = client.post("/messages/", json=payload)
    assert send_resp.status_code == 201
    message_id = send_resp.json()["id"]

    # Get unread messages
    unread_resp = client.get(f"/messages/unread/{recipient['email']}")
    assert unread_resp.status_code == 200
    unread = unread_resp.json()
    assert any(m["id"] == message_id for m in unread)

    # Mark as read
    client.patch(
        f"/messages/read/{message_id}",
        params={"recipient_email": recipient["email"]}
    )

    unread_resp2 = client.get(f"/messages/unread/{recipient['email']}")
    assert unread_resp2.status_code == 200
    unread2 = unread_resp2.json()
    assert all(m["id"] != message_id for m in unread2)

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def users():
    sender = {"email": "sender@example.com", "name": "Sender"}
    recipient1 = {"email": "recipient1@example.com", "name": "Recipient One"}
    recipient2 = {"email": "recipient2@example.com", "name": "Recipient Two"}
    client.post("/users/", json=sender)
    client.post("/users/", json=recipient1)
    client.post("/users/", json=recipient2)
    return sender, recipient1, recipient2

@pytest.fixture
def sample_message(users):
    sender, recipient1, recipient2 = users
    payload = {
        "sender_email": sender["email"],
        "recipient_emails": [recipient1["email"], recipient2["email"]],
        "subject": "Sample Subject",
        "content": "Sample message content."
    }
    resp = client.post("/messages/", json=payload)
    assert resp.status_code == 201
    message_id = resp.json()["id"]
    return message_id, users

def test_send_message(users):
    sender, recipient1, recipient2 = users
    payload = {
        "sender_email": sender["email"],
        "recipient_emails": [recipient1["email"], recipient2["email"]],
        "subject": "Test Subject",
        "content": "Hello, this is a test message."
    }
    response = client.post("/messages/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["sender_email"] == sender["email"]
    assert recipient1["email"] in data["recipient_emails"]
    assert recipient2["email"] in data["recipient_emails"]
    assert data["subject"] == "Test Subject"
    assert data["content"] == "Hello, this is a test message."
    assert "id" in data

def test_get_inbox(sample_message):
    message_id, (sender, recipient1, recipient2) = sample_message
    response = client.get(f"/messages/inbox/{recipient1['email']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(msg["id"] == message_id for msg in data)

def test_get_sent(sample_message):
    message_id, (sender, recipient1, recipient2) = sample_message
    response = client.get(f"/messages/sent/{sender['email']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(msg["id"] == message_id for msg in data)

def test_mark_message_as_read(sample_message):
    message_id, (sender, recipient1, recipient2) = sample_message
    patch_resp = client.patch(
        f"/messages/read/{message_id}",
        params={"recipient_email": recipient1["email"]}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["detail"] == "Message marked as read successfully"

    # Check that the message is now marked as read in inbox
    inbox_resp = client.get(f"/messages/inbox/{recipient1['email']}")
    assert inbox_resp.status_code == 200
    inbox = inbox_resp.json()
    msg = next((m for m in inbox if m["id"] == message_id), None)
    assert msg is not None
    assert msg["read"] is True

def test_get_unread_messages(sample_message):
    message_id, (sender, recipient1, recipient2) = sample_message

    unread_resp = client.get(f"/messages/unread/{recipient2['email']}")
    assert unread_resp.status_code == 200
    unread = unread_resp.json()
    assert any(m["id"] == message_id for m in unread)

    client.patch(
        f"/messages/read/{message_id}",
        params={"recipient_email": recipient2["email"]}
    )

    unread_resp2 = client.get(f"/messages/unread/{recipient2['email']}")
    assert unread_resp2.status_code == 200
    unread2 = unread_resp2.json()
    assert all(m["id"] != message_id for m in unread2)

def test_get_message_with_recipients(sample_message):
    message_id, (sender, recipient1, recipient2) = sample_message
    response = client.get(f"/messages/{message_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == message_id
    assert data["sender_email"] == sender["email"]
    assert "recipients" in data
    recipient_emails = [r["email"] for r in data["recipients"]]
    assert recipient1["email"] in recipient_emails
    assert recipient2["email"] in recipient_emails

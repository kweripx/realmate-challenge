from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import uuid
from .models import Conversation, Message
import json
from datetime import datetime
from django.utils import timezone
# Create your tests here.


class WebhookTestCase(TestCase):
    def setUp(self):
        # Initialize the APIClient
        self.client = APIClient()
        # URL for the webhook endpoint
        self.webhook_url = reverse("webhook")

        # Create a valid ID for the conversation
        self.conversation_id = uuid.uuid4()

        # Create a valid ID for the message
        self.message_id = uuid.uuid4()

    def test_create_new_conversation(self):
        """Test that a new conversation is created"""
        # Create a new conversation
        payload = {
            "type": "NEW_CONVERSATION",
            "timestamp": "2025-03-01T10:20:41.349308",
            "data": {"id": str(self.conversation_id)},
        }
        response = self.client.post(
            self.webhook_url, json.dumps(payload), content_type="application/json"
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the conversation was created
        self.assertTrue(Conversation.objects.filter(id=self.conversation_id).exists())

        # Check that the conversation is open
        conversation = Conversation.objects.get(id=self.conversation_id)
        self.assertEqual(conversation.status, Conversation.OPEN)

    def test_add_message_to_conversation(self):
        """Test that a new message is added to a conversation"""
        # Create a new conversation
        conversation = Conversation.objects.create(id=self.conversation_id)

        # Add a new message to the conversation
        payload = {
            "type": "NEW_MESSAGE",
            "timestamp": "2025-03-01T10:20:41.349308",
            "data": {
                "id": str(self.message_id),
                "conversation_id": str(self.conversation_id),
                "content": "Hello, world!",
                "direction": "RECEIVED",
            },
        }
        response = self.client.post(
            self.webhook_url, json.dumps(payload), content_type="application/json"
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the message was created
        self.assertTrue(Message.objects.filter(id=self.message_id).exists())

        # Check that the message is associated with the correct conversation
        message = Message.objects.get(id=self.message_id)
        self.assertEqual(str(message.conversation.id), str(self.conversation_id))
        self.assertEqual(message.content, "Hello, world!")
        self.assertEqual(message.direction, Message.RECEIVED)

    def test_close_conversation(self):
        """Test that a conversation is closed"""
        # Create a new conversation
        conversation = Conversation.objects.create(id=self.conversation_id)

        # Close the conversation
        payload = {
            "type": "CLOSE_CONVERSATION",
            "timestamp": "2025-02-21T10:20:45.349308",
            "data": {"id": str(self.conversation_id)},
        }
        response = self.client.post(
            self.webhook_url, json.dumps(payload), content_type="application/json"
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the conversation status was updated to closed
        conversation.refresh_from_db()
        self.assertEqual(conversation.status, Conversation.CLOSED)

    def test_add_message_to_closed_conversation(self):
        """Test that a message is not added to a closed conversation"""
        # Create a new conversation
        conversation = Conversation.objects.create(
            id=self.conversation_id, status=Conversation.CLOSED
        )

        # Add a new message to the conversation
        payload = {
            "type": "NEW_MESSAGE",
            "timestamp": "2025-02-21T10:20:42.349308",
            "data": {
                "id": str(self.message_id),
                "direction": "RECEIVED",
                "content": "This message should not be accepted",
                "conversation_id": str(self.conversation_id),
            },
        }

        response = self.client.post(
            self.webhook_url, data=json.dumps(payload), content_type="application/json"
        )

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the message was not created
        self.assertFalse(Message.objects.filter(id=self.message_id).exists())

    def test_message_to_nonexistent_conversation(self):
        """Test that it is not possible to add a message to a nonexistent conversation"""
        # Generate an ID for a nonexistent conversation
        nonexistent_id = uuid.uuid4()

        # Payload to try to add a message
        payload = {
            "type": "NEW_MESSAGE",
            "timestamp": "2025-02-21T10:20:42.349308",
            "data": {
                "id": str(self.message_id),
                "direction": "RECEIVED",
                "content": "This message should not be accepted",
                "conversation_id": str(nonexistent_id),
            },
        }

        response = self.client.post(
            self.webhook_url, data=json.dumps(payload), content_type="application/json"
        )

        # Check that the response is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Check that the message was not created
        self.assertFalse(Message.objects.filter(id=self.message_id).exists())


class ConversationDetailTests(TestCase):
    def setUp(self):
        # Initialize the API test client
        self.client = APIClient()

        # Create a conversation with messages for testing
        self.conversation_id = uuid.uuid4()
        self.conversation = Conversation.objects.create(id=self.conversation_id)

        # Create some messages associated with the conversation
        self.message1_id = uuid.uuid4()
        self.message2_id = uuid.uuid4()

        Message.objects.create(
            id=self.message1_id,
            conversation=self.conversation,
            content="Olá, tudo bem?",
            direction=Message.RECEIVED,
            timestamp=timezone.make_aware(
                datetime.fromisoformat("2025-02-21T10:20:42.349308")
            ),
        )

        Message.objects.create(
            id=self.message2_id,
            conversation=self.conversation,
            content="Tudo ótimo e você?",
            direction=Message.SENT,
            timestamp=timezone.make_aware(
                datetime.fromisoformat("2025-02-21T10:20:44.349308")
            ),
        )

    def test_get_conversation_detail(self):
        """Test that it is possible to get the details of an existing conversation"""
        url = reverse("conversation-detail", kwargs={"id": self.conversation_id})
        response = self.client.get(url)

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the content of the response
        data = response.json()
        self.assertEqual(str(data["id"]), str(self.conversation_id))
        self.assertEqual(data["status"], Conversation.OPEN)
        self.assertEqual(len(data["messages"]), 2)

        # Check the first message
        messages = sorted(data["messages"], key=lambda m: m["timestamp"])
        self.assertEqual(str(messages[0]["id"]), str(self.message1_id))
        self.assertEqual(messages[0]["content"], "Olá, tudo bem?")
        self.assertEqual(messages[0]["direction"], Message.RECEIVED)

        # Check the second message
        self.assertEqual(str(messages[1]["id"]), str(self.message2_id))
        self.assertEqual(messages[1]["content"], "Tudo ótimo e você?")
        self.assertEqual(messages[1]["direction"], Message.SENT)

    def test_get_nonexistent_conversation(self):
        """Test that it is not possible to get the details of a nonexistent conversation"""
        nonexistent_id = uuid.uuid4()
        url = reverse("conversation-detail", kwargs={"id": nonexistent_id})
        response = self.client.get(url)

        # Check that the response is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Conversation, Message
from .serializers import ConversationSerializer
from datetime import datetime
import json


class WebhookView(APIView):
    def post(self, request):
        try:
            # Verify event type
            event_type = request.data.get("type")
            timestamp = request.data.get("timestamp")
            data = request.data.get("data")

            if not all([event_type, timestamp, data]):
                return Response(
                    {"error": "Missing data from webhook"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Convert timestamp to datetime object
            event_time = timezone.make_aware(datetime.fromisoformat(timestamp))

            if event_type == "NEW_CONVERSATION":
                # Create new conversation
                conversation_id = data.get("id")
                conversation = Conversation.objects.create(
                    id=conversation_id, status=Conversation.OPEN
                )
                return Response(
                    {"message": "New conversation created"},
                    status=status.HTTP_201_CREATED,
                )

            elif event_type == "NEW_MESSAGE":
                # Create new message
                conversation_id = data.get("conversation_id")
                message_id = data.get("id")
                content = data.get("content")
                direction = data.get("direction")

                # Check if every required field is present
                if not all([conversation_id, message_id, content, direction]):
                    return Response(
                        {"error": "Missing required fields"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Find the conversation
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    return Response(
                        {"error": "Conversation not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Check if the conversation is open
                if conversation.status != Conversation.OPEN:
                    return Response(
                        {"error": "Conversation is not open"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Create new message
                Message.objects.create(
                    id=message_id,
                    conversation=conversation,
                    content=content,
                    direction=direction,
                    timestamp=event_time,
                )
                return Response(
                    {"status": "Message created successfully"},
                    status=status.HTTP_201_CREATED,
                )

            elif event_type == "CLOSE_CONVERSATION":
                # Update conversation status
                conversation_id = data.get("id")
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    conversation.status = Conversation.CLOSED
                    conversation.save()
                    return Response(
                        {"status": "Conversation closed successfully"},
                        status=status.HTTP_200_OK,
                    )
                except Conversation.DoesNotExist:
                    return Response(
                        {"error": "Conversation not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            return Response(
                {"error": "Invalid event type"}, status=status.HTTP_400_BAD_REQUEST
            )
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON payload"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log the error
            print(f"Error: {e}")
            return Response(
                {"error": "An error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConversationDetailView(RetrieveAPIView):
    serializer_class = ConversationSerializer

    def get_object(self):
        conversation_id = self.kwargs.get("id")
        return get_object_or_404(Conversation, id=conversation_id)

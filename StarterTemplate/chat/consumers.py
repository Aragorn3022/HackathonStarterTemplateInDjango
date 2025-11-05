# filepath: g:\HackathonStarterTemplateInDjango\StarterTemplate\chat\consumers.py
"""
WebSocket consumer for real-time chat functionality.
Handles WebSocket connections, message broadcasting, and authentication.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from .encryption import encrypt_message, decrypt_message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for 1-on-1 chat.
    Each chat room has a unique group name for broadcasting messages.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Get room_id from URL route
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Get user from scope (set by AuthMiddlewareStack)
        self.user = self.scope.get('user')
        
        # Check authentication
        if not self.user or not hasattr(self.user, 'id'):
            # Reject connection if not authenticated
            await self.close()
            return
        
        # Verify user has access to this chat room
        has_access = await self.verify_room_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the WebSocket connection
        await self.accept()
        
        # Send a connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat room'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        Expected format: {'message': 'text content'}
        """
        try:
            data = json.loads(text_data)
            message_content = data.get('message', '').strip()
            
            if not message_content:
                return
            
            # Save message to database (encrypted)
            message_data = await self.save_message(message_content)
            
            if message_data:
                # Broadcast message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message_data['content'],
                        'sender_id': str(message_data['sender_id']),
                        'sender_username': message_data['sender_username'],
                        'timestamp': message_data['timestamp'],
                        'message_id': str(message_data['message_id'])
                    }
                )
        except json.JSONDecodeError:
            # Invalid JSON
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
        except Exception as e:
            # Log error and send error message
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to send message'
            }))
    
    async def chat_message(self, event):
        """
        Receive message from room group and send to WebSocket.
        This is called when a message is broadcast to the group.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))
    
    @database_sync_to_async
    def verify_room_access(self):
        """Verify that the user has access to this chat room"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            # Check if user is part of this chat room
            return (str(room.user1.id) == str(self.user.id) or 
                    str(room.user2.id) == str(self.user.id))
        except ChatRoom.DoesNotExist:
            return False
        except Exception:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """
        Save message to database with encryption.
        Returns message data for broadcasting.
        """
        try:
            from accounts.models import User
            
            # Get the chat room
            room = ChatRoom.objects.get(id=self.room_id)
            
            # Get the sender user object
            sender = User.objects.get(id=self.user.id)
            
            # Create and save message (encrypted)
            message = Message.create_message(
                room=room,
                sender=sender,
                content=content
            )
            
            # Return message data for broadcasting
            return {
                'content': content,  # Send decrypted content over WebSocket
                'sender_id': str(sender.id),
                'sender_username': sender.username,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'message_id': str(message.id)
            }
        except Exception as e:
            # Log the error (in production, use proper logging)
            print(f"Error saving message: {e}")
            return None

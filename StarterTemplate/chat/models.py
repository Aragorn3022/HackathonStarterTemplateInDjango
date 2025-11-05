from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, BooleanField
from datetime import datetime
from accounts.models import User
from .encryption import encrypt_message, decrypt_message


class ChatRoom(Document):
    """
    Chat room between two users (private 1-on-1 chat)
    """
    user1 = ReferenceField(User, required=True)
    user2 = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.now)
    last_message_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'chat_rooms',
        'indexes': [
            {'fields': ['user1', 'user2'], 'unique': True},
            'created_at',
            'last_message_at'
        ],
    }
    
    def __str__(self):
        return f"Chat: {self.user1.username} <-> {self.user2.username}"
    
    @classmethod
    def get_or_create_room(cls, user1, user2):
        """
        Get existing chat room or create new one between two users.
        Ensures consistent ordering (lower user id first)
        """
        # Ensure consistent ordering to avoid duplicate rooms
        if str(user1.id) > str(user2.id):
            user1, user2 = user2, user1
        
        # Try to find existing room
        room = cls.objects(user1=user1, user2=user2).first()
        
        if not room:
            room = cls(user1=user1, user2=user2)
            room.save()
        
        return room
    
    def get_other_user(self, current_user):
        """
        Get the other user in the chat (not the current user)
        """
        if str(self.user1.id) == str(current_user.id):
            return self.user2
        return self.user1
    
    def get_messages(self, limit=50):
        """
        Get recent messages in this room (decrypted)
        """
        messages = Message.objects(room=self).order_by('-timestamp')[:limit]
        # Decrypt messages
        for msg in messages:
            msg.decrypted_content = decrypt_message(msg.encrypted_content)
        return list(reversed(messages))


class Message(Document):
    """
    Individual chat message (encrypted)
    """
    room = ReferenceField(ChatRoom, required=True)
    sender = ReferenceField(User, required=True)
    encrypted_content = StringField(required=True)  # AES256 encrypted message
    timestamp = DateTimeField(default=datetime.now)
    is_read = BooleanField(default=False)
    
    meta = {
        'collection': 'chat_messages',
        'indexes': [
            {'fields': ['-timestamp']},
            'room',
            'sender',
            'is_read'
        ],
    }
    
    def __str__(self):
        return f"{self.sender.username}: [Encrypted]"
    
    @classmethod
    def create_message(cls, room, sender, content):
        """
        Create and save a new encrypted message
        """
        encrypted = encrypt_message(content)
        message = cls(
            room=room,
            sender=sender,
            encrypted_content=encrypted
        )
        message.save()
        
        # Update room's last_message_at
        room.last_message_at = datetime.now()
        room.save()
        
        return message
    
    def get_decrypted_content(self):
        """
        Decrypt and return the message content
        """
        return decrypt_message(self.encrypted_content)
    
    def mark_as_read(self):
        """
        Mark message as read
        """
        self.is_read = True
        self.save()

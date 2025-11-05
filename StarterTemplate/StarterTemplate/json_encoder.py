"""
Custom JSON encoder for MongoEngine objects in Django sessions
"""
from django.core.serializers.json import DjangoJSONEncoder
from bson import ObjectId
from datetime import datetime


class MongoEngineJSONEncoder(DjangoJSONEncoder):
    """
    Custom JSON encoder that handles MongoEngine-specific types
    """
    
    def default(self, obj):
        # Handle ObjectId
        if isinstance(obj, ObjectId):
            return str(obj)
        
        # Handle datetime (MongoEngine uses datetime)
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # Handle MongoEngine Document objects
        if hasattr(obj, 'to_mongo'):
            # Convert MongoEngine document to dict
            return obj.to_mongo().to_dict()
        
        # Fallback to default serialization
        return super().default(obj)

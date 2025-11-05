"""
Custom session serializer for MongoEngine objects
"""
import json
from django.core.signing import JSONSerializer as BaseJSONSerializer
from .json_encoder import MongoEngineJSONEncoder


class MongoEngineSessionSerializer(BaseJSONSerializer):
    """
    Custom session serializer that uses MongoEngineJSONEncoder
    to handle MongoEngine objects in sessions
    """
    
    def dumps(self, obj):
        return json.dumps(
            obj,
            separators=(",", ":"),
            cls=MongoEngineJSONEncoder
        ).encode("latin-1")

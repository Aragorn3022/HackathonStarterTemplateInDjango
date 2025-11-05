# filepath: g:\HackathonStarterTemplateInDjango\StarterTemplate\chat\routing.py
"""
WebSocket URL routing for the chat application.
Defines WebSocket URL patterns similar to Django's URL patterns.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]

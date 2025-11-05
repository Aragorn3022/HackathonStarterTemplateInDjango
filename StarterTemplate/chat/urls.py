"""
Chat URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('search/', views.search_user, name='search_user'),
    path('room/<str:room_id>/', views.chat_room, name='chat_room'),
    path('delete/<str:room_id>/', views.delete_chat, name='delete_chat'),
    path('api/messages/<str:room_id>/', views.get_messages_api, name='get_messages_api'),
]

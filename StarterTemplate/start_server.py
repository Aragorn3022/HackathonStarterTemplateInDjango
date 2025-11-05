#!/usr/bin/env python
"""
Start the Django server with proper ASGI/WebSocket support.
This script ensures Daphne is used for WebSocket connections.
"""
import os
import sys
import subprocess

def main():
    """Start the Django server with Daphne"""
    
    print("=" * 70)
    print("🚀 Starting Django Server with WebSocket Support (Daphne)")
    print("=" * 70)
    
    # Check if in correct directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found!")
        print("Please run this script from the StarterTemplate directory.")
        sys.exit(1)
    
    # Check if daphne is installed
    try:
        import daphne
        print(f"✅ Daphne version: {daphne.__version__}")
    except ImportError:
        print("❌ Daphne not installed!")
        print("Installing daphne...")
        subprocess.run([sys.executable, "-m", "pip", "install", "daphne"], check=True)
        print("✅ Daphne installed successfully!")
    
    # Check if MongoDB is accessible (optional warning)
    try:
        from mongoengine import connect
        from django.conf import settings
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StarterTemplate.settings')
        import django
        django.setup()
        
        from chat.models import ChatRoom
        ChatRoom.objects.count()
        print("✅ MongoDB connection: OK")
    except Exception as e:
        print(f"⚠️  Warning: MongoDB connection issue: {e}")
        print("Make sure MongoDB is running: mongod")
    
    print("\n" + "=" * 70)
    print("🌐 Server will start at: http://127.0.0.1:8000")
    print("📡 WebSocket endpoint: ws://127.0.0.1:8000/ws/chat/<room_id>/")
    print("=" * 70)
    print("\n💡 Press Ctrl+C to stop the server\n")
    
    # Start Daphne
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "daphne",
            "-b", "0.0.0.0",
            "-p", "8000",
            "StarterTemplate.asgi:application"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped!")
        sys.exit(0)

if __name__ == "__main__":
    main()

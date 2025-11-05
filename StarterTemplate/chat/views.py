from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import User
from .models import ChatRoom, Message
from .forms import MessageForm, SearchUserForm
from bson import ObjectId


@login_required
def chat_home(request):
    """
    Display list of chat rooms for current user
    """
    current_user = User.objects.get(id=str(request.user.id))
    
    # Get all chat rooms where current user is participant
    rooms_as_user1 = ChatRoom.objects(user1=current_user).order_by('-last_message_at')
    rooms_as_user2 = ChatRoom.objects(user2=current_user).order_by('-last_message_at')
    
    # Combine and sort by last_message_at
    all_rooms = list(rooms_as_user1) + list(rooms_as_user2)
    all_rooms.sort(key=lambda x: x.last_message_at, reverse=True)
    
    # Add additional info to each room
    for room in all_rooms:
        room.other_user = room.get_other_user(current_user)
        # Get last message
        last_msg = Message.objects(room=room).order_by('-timestamp').first()
        if last_msg:
            room.last_message = last_msg.get_decrypted_content()[:50] + '...' if len(last_msg.get_decrypted_content()) > 50 else last_msg.get_decrypted_content()
        else:
            room.last_message = 'No messages yet'
        
        # Count unread messages
        unread_count = Message.objects(room=room, is_read=False).filter(sender__ne=current_user).count()
        room.unread_count = unread_count
    
    search_form = SearchUserForm()
    
    return render(request, 'chat/chat_home.html', {
        'rooms': all_rooms,
        'search_form': search_form
    })


@login_required
def search_user(request):
    """
    Search for a user to start a chat with
    """
    if request.method == 'POST':
        form = SearchUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            
            try:
                other_user = User.objects.get(username=username)
                
                # Can't chat with yourself
                if str(other_user.id) == str(request.user.id):
                    messages.error(request, "You can't chat with yourself!")
                    return redirect('chat_home')
                
                # Get or create chat room
                current_user = User.objects.get(id=str(request.user.id))
                room = ChatRoom.get_or_create_room(current_user, other_user)
                
                return redirect('chat_room', room_id=str(room.id))
                
            except User.DoesNotExist:
                messages.error(request, f'User "{username}" not found.')
                return redirect('chat_home')
    
    return redirect('chat_home')


@login_required
def chat_room(request, room_id):
    """
    Display chat room and handle message sending
    """
    current_user = User.objects.get(id=str(request.user.id))
    
    # Get chat room
    try:
        room = ChatRoom.objects.get(id=ObjectId(room_id))
    except ChatRoom.DoesNotExist:
        messages.error(request, 'Chat room not found.')
        return redirect('chat_home')
    
    # Verify user has access to this room
    if str(room.user1.id) != str(current_user.id) and str(room.user2.id) != str(current_user.id):
        messages.error(request, 'You do not have access to this chat room.')
        return redirect('chat_home')
    
    # Get the other user
    other_user = room.get_other_user(current_user)
    
    # Handle message sending
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['message']
            
            # Create encrypted message
            Message.create_message(room, current_user, content)
            
            messages.success(request, 'Message sent!')
            return redirect('chat_room', room_id=room_id)
    else:
        form = MessageForm()
    
    # Get messages (decrypted)
    chat_messages = room.get_messages(limit=100)
    
    # Mark unread messages as read
    unread_messages = Message.objects(room=room, sender=other_user, is_read=False)
    for msg in unread_messages:
        msg.mark_as_read()
    
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'other_user': other_user,
        'messages': chat_messages,
        'form': form,
        'current_user': current_user
    })


@login_required
def delete_chat(request, room_id):
    """
    Delete a chat room and all its messages
    """
    current_user = User.objects.get(id=str(request.user.id))
    
    try:
        room = ChatRoom.objects.get(id=ObjectId(room_id))
        
        # Verify user has access
        if str(room.user1.id) != str(current_user.id) and str(room.user2.id) != str(current_user.id):
            messages.error(request, 'You do not have access to this chat room.')
            return redirect('chat_home')
        
        # Delete all messages in the room
        Message.objects(room=room).delete()
        
        # Delete the room
        room.delete()
        
        messages.success(request, 'Chat deleted successfully!')
    except ChatRoom.DoesNotExist:
        messages.error(request, 'Chat room not found.')
    
    return redirect('chat_home')


@login_required
def get_messages_api(request, room_id):
    """
    API endpoint to get messages (for AJAX polling)
    """
    current_user = User.objects.get(id=str(request.user.id))
    
    try:
        room = ChatRoom.objects.get(id=ObjectId(room_id))
        
        # Verify access
        if str(room.user1.id) != str(current_user.id) and str(room.user2.id) != str(current_user.id):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get messages
        messages_list = room.get_messages(limit=100)
        
        # Format for JSON
        messages_data = []
        for msg in messages_list:
            messages_data.append({
                'id': str(msg.id),
                'sender': msg.sender.username,
                'content': msg.decrypted_content,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'is_current_user': str(msg.sender.id) == str(current_user.id)
            })
        
        return JsonResponse({'messages': messages_data})
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

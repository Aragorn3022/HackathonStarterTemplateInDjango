from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    UserPasswordChangeSerializer,
    UserLoginSerializer,
    UserListSerializer,
    UserDetailSerializer
)


class UserPagination(PageNumberPagination):
    """Custom pagination for user list"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """
    Register a new user
    POST /api/register/
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Return user data
        user_data = UserSerializer(user).data
        
        return Response({
            'message': 'User registered successfully',
            'user': user_data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    Login user
    POST /api/login/
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    # Authenticate user
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user, backend='accounts.auth_backend.MongoEngineBackend')
        user.update_last_login()
        
        # Return user data
        user_data = UserSerializer(user).data
        
        return Response({
            'message': 'Login successful',
            'user': user_data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid username or password'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    Logout user
    POST /api/logout/
    """
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    """
    Get current user profile
    GET /api/profile/
    """
    try:
        # Get user from MongoDB
        user = User.objects.get(id=str(request.user.id))
        serializer = UserSerializer(user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_update_profile(request):
    """
    Update current user profile
    PUT/PATCH /api/profile/update/
    """
    try:
        # Get user from MongoDB
        user = User.objects.get(id=str(request.user.id))
        
        # Partial update for PATCH, full update for PUT
        partial = request.method == 'PATCH'
        serializer = UserUpdateSerializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            
            # Return updated user data
            updated_user = UserSerializer(user).data
            
            return Response({
                'message': 'Profile updated successfully',
                'user': updated_user
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    """
    Change user password
    POST /api/profile/change-password/
    """
    try:
        # Get user from MongoDB
        user = User.objects.get(id=str(request.user.id))
        
        serializer = UserPasswordChangeSerializer(
            data=request.data,
            context={'user': user}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_list(request):
    """
    List all users (with pagination)
    GET /api/users/
    """
    users = User.objects.all()
    
    # Apply pagination
    paginator = UserPagination()
    paginated_users = paginator.paginate_queryset(users, request)
    
    serializer = UserListSerializer(paginated_users, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_detail(request, user_id):
    """
    Get user detail by ID
    GET /api/users/<user_id>/
    """
    try:
        user = User.objects.get(id=user_id)
        serializer = UserDetailSerializer(user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_account(request):
    """
    Delete current user account
    DELETE /api/profile/delete/
    """
    try:
        # Get user from MongoDB
        user = User.objects.get(id=str(request.user.id))
        
        # Logout before deleting
        logout(request)
        
        # Delete user
        user.delete()
        
        return Response({
            'message': 'Account deleted successfully'
        }, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_check_username(request):
    """
    Check if username is available
    GET /api/check-username/?username=<username>
    """
    username = request.query_params.get('username')
    
    if not username:
        return Response({
            'error': 'Username parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    exists = User.objects(username=username).first() is not None
    
    return Response({
        'username': username,
        'available': not exists
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_check_email(request):
    """
    Check if email is available
    GET /api/check-email/?email=<email>
    """
    email = request.query_params.get('email')
    
    if not email:
        return Response({
            'error': 'Email parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    exists = User.objects(email=email).first() is not None
    
    return Response({
        'email': email,
        'available': not exists
    }, status=status.HTTP_200_OK)

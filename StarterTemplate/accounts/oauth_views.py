# filepath: g:\HackathonStarterTemplateInDjango\StarterTemplate\accounts\oauth_views.py
"""
Google OAuth authentication views
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import os

from .models import User
from .auth_utils import login as auth_login
from .email_utils import send_welcome_email


# OAuth 2.0 client configuration
# Note: redirect_uri is dynamically set in the views to support both HTTP and HTTPS
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv('GOOGLE_OAUTH_CLIENT_ID', ''),
        "client_secret": os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', ''),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": []  # Set dynamically based on request
    }
}

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


def google_login(request):
    """
    Initiate Google OAuth flow
    """
    # Check if OAuth is configured
    if not CLIENT_CONFIG['web']['client_id'] or not CLIENT_CONFIG['web']['client_secret']:
        messages.error(request, 'Google OAuth is not configured. Please contact administrator.')
        return redirect('login')
    
    try:
        # Create flow
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=request.build_absolute_uri(reverse('google_callback'))
        )
        
        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='select_account'
        )
        
        # Store state in session for verification
        request.session['oauth_state'] = state
        
        return redirect(authorization_url)
    
    except Exception as e:
        messages.error(request, f'Error initiating Google login: {str(e)}')
        return redirect('login')


def google_callback(request):
    """
    Handle Google OAuth callback
    """
    try:
        # Verify state
        state = request.session.get('oauth_state')
        if not state or state != request.GET.get('state'):
            messages.error(request, 'Invalid OAuth state. Please try again.')
            return redirect('login')
        
        # Check for errors
        error = request.GET.get('error')
        if error:
            messages.error(request, f'Google authentication failed: {error}')
            return redirect('login')
        
        # Exchange code for credentials
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=request.build_absolute_uri(reverse('google_callback')),
            state=state
        )
        
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        
        # Get user info from ID token
        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            CLIENT_CONFIG['web']['client_id']
        )
        
        # Extract user information
        google_id = id_info.get('sub')
        email = id_info.get('email')
        email_verified = id_info.get('email_verified', False)
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        profile_picture = id_info.get('picture')
        
        # Verify email is verified by Google
        if not email_verified:
            messages.error(request, 'Your Google email is not verified. Please verify it first.')
            return redirect('login')
        
        # Get or create user
        user, is_new = User.get_or_create_oauth_user(
            provider='google',
            oauth_id=google_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            profile_picture=profile_picture
        )
        
        # Clean up session
        if 'oauth_state' in request.session:
            del request.session['oauth_state']
        
        # Log the user in
        auth_login(request, user, backend='accounts.auth_backend.MongoEngineBackend')
        user.update_last_login()
          # Send welcome email for new users
        if is_new:
            send_welcome_email(user, request)
            messages.success(request, f'Welcome, {user.first_name or user.username}! Your account has been created via Google.')
        else:
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        
        return redirect('profile')
    
    except Exception as e:
        messages.error(request, f'Error during Google authentication: {str(e)}')
        return redirect('login')

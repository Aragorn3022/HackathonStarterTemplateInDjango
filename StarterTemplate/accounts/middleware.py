from .models import User
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth import SESSION_KEY


class MongoEngineUserMiddleware:
    """
    Middleware to attach MongoEngine User object to request
    This replaces Django's default authentication middleware for MongoEngine users
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if there's a user ID in the session
        if SESSION_KEY in request.session:
            user_id = request.session[SESSION_KEY]
            try:
                # Try to get MongoEngine user
                mongo_user = User.objects.get(id=user_id)
                request.user = mongo_user
            except User.DoesNotExist:
                # If user doesn't exist, clear the session
                request.session.flush()
                from django.contrib.auth.models import AnonymousUser
                request.user = AnonymousUser()
        else:
            # No user in session, set anonymous user
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response

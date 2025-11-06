from .models import User


class MongoEngineBackend:
    """
    Custom authentication backend for MongoEngine User model
    """
    
    def authenticate(self, request, username=None, password=None):
        """
        Authenticate a user with username and password.
        OAuth users (without password) cannot authenticate this way.
        """
        try:
            user = User.objects.get(username=username)
            # Check if user has a password (not OAuth user)
            if user.password and user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        """
        Get a user by their ID
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

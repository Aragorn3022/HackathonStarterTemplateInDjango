from .models import User


class MongoEngineBackend:
    """
    Custom authentication backend for MongoEngine User model
    """
    
    def authenticate(self, request, username=None, password=None):
        """
        Authenticate a user with username and password
        """
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
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

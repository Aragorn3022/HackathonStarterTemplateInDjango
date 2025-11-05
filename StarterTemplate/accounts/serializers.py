from rest_framework_mongoengine.serializers import serializers
from .models import User
import rest_framework_mongoengine

class UserSerializer(rest_framework_mongoengine.serializers.DocumentSerializer):
    """
    Serializer for User model - Full user data
    """
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login'
        ]
        read_only_fields = [ 'date_joined', 'last_login']


class UserRegistrationSerializer(rest_framework_mongoengine.serializers.DocumentSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text='Password must be at least 6 characters long.'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Confirm your password.'
    )
    
    class Meta:
        model = User
        fields = [
            
            'username',
            'email',
            'first_name',
            'last_name',            'password',
            'password_confirm'
        ]
        read_only_fields = ['id']        
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }
    
    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects(username=value).first():
            raise serializers.ValidationError('This username is already taken.')
        return value
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects(email=value).first():
            raise serializers.ValidationError('This email is already registered.')
        return value
    
    def validate(self, data):
        """Validate that passwords match"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return data
    
    def create(self, validated_data):
        """Create a new user with hashed password"""
        # Remove password_confirm from validated data
        validated_data.pop('password_confirm', None)
        
        # Extract password
        password = validated_data.pop('password')
        
        # Create user
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserUpdateSerializer(rest_framework_mongoengine.serializers.DocumentSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email'
        ]
    
    def validate_email(self, value):
        """Check if email is already used by another user"""
        user = self.instance
        if user and User.objects(email=value).exclude(id=user.id).first():
            raise serializers.ValidationError('This email is already registered.')
        return value


class UserPasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text='New password must be at least 6 characters long.'
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password is correct"""
        user = self.context.get('user')
        if not user or not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
    
    def validate(self, data):
        """Validate that new passwords match"""
        if data.get('new_password') != data.get('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return data
    
    def save(self):
        """Update user password"""
        user = self.context.get('user')
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class UserListSerializer(rest_framework_mongoengine.serializers.DocumentSerializer):
    """
    Serializer for listing users (minimal data)
    """
    class Meta:
        model = User
        fields = [
            
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'date_joined'
        ]
        read_only_fields = fields


class UserDetailSerializer(rest_framework_mongoengine.serializers.DocumentSerializer):
    """
    Serializer for user detail view (public profile)
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            
            'username',
            'first_name',
            'last_name',
            'full_name',
            'is_active',
            'date_joined'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        """Get user's full name"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username

from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField, IntField
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import salted_hmac
from django.conf import settings
from datetime import datetime, timedelta
import random

# Create your models here.
class User(Document):
    """
    Custom User model using MongoEngine Document.
    Compatible with Django authentication but does not inherit from Django's User model.
    """
    username = StringField(required=True, max_length=50, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    first_name = StringField(max_length=30, default='')
    last_name = StringField(max_length=30, default='')
    is_active = BooleanField(default=False)  # Changed to False until OTP verification
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    is_verified = BooleanField(default=False)  # Email verification status
    date_joined = DateTimeField(default=datetime.now)
    last_login = DateTimeField(default=None)
    
    # OTP fields
    otp_code = StringField(max_length=6, default=None)
    otp_created_at = DateTimeField(default=None)
    otp_attempts = IntField(default=0)
    
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email'],
    }
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
    def check_password(self, raw_password):
        """Check if the provided password is correct"""
        return check_password(raw_password, self.password)    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.now()
        self.save()
    
    def __str__(self):
        return self.username
    
    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False for real users"""
        return False
    
    def get_username(self):
        """Return the username for this User"""
        return self.username
    
    @property
    def pk(self):
        """Return primary key (ObjectId as string) for Django compatibility"""
        return str(self.id) if self.id else None
    
    def get_session_auth_hash(self):
        """
        Return an HMAC of the password field for session validation.
        This is used by Django to invalidate sessions when password changes.
        """
        key_salt = "accounts.models.User.get_session_auth_hash"
        return salted_hmac(
            key_salt,
            self.password,
            secret=settings.SECRET_KEY,
            algorithm='sha256',
        ).hexdigest()
    def get_session_auth_fallback_hash(self):
        """
        Return fallback hashes for old secret keys.
        This allows sessions to remain valid during key rotation.
        """
        for fallback_secret in settings.SECRET_KEY_FALLBACKS:
            yield salted_hmac(
                "accounts.models.User.get_session_auth_hash",
                self.password,
                secret=fallback_secret,
                algorithm='sha256',
            ).hexdigest()
    
    # Permission-related methods (normally from PermissionsMixin)
    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission.
        Superusers have all permissions.
        """
        if self.is_active and self.is_superuser:
            return True
        # For now, we're not implementing granular permissions
        # You can extend this to check against a permissions collection
        return False
    
    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)
    
    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Superusers have all permissions.
        """
        if self.is_active and self.is_superuser:
            return True
        # For now, we're not implementing granular permissions
        return False
    
    def get_all_permissions(self, obj=None):
        """
        Return a set of permission strings that this user has.
        Superusers have all permissions.
        """
        if self.is_superuser:
            return set(['all'])
        return set()
    
    def get_group_permissions(self, obj=None):
        """
        Return a set of permission strings that this user has through their groups.
        """
        # Groups not implemented for MongoEngine users
        return set()
    
    # OTP Methods
    def generate_otp(self):
        """Generate a 6-digit OTP code"""
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_created_at = datetime.now()
        self.otp_attempts = 0
        self.save()
        return self.otp_code
    
    def verify_otp(self, otp_code):
        """Verify the OTP code"""
        # Check if OTP exists
        if not self.otp_code:
            return False, "No OTP code found. Please request a new one."
        
        # Check if OTP has expired (10 minutes)
        if self.otp_created_at:
            expiry_time = self.otp_created_at + timedelta(minutes=10)
            if datetime.now() > expiry_time:
                return False, "OTP has expired. Please request a new one."
        
        # Check attempts limit
        if self.otp_attempts >= 3:
            return False, "Too many failed attempts. Please request a new OTP."
        
        # Verify OTP
        if self.otp_code == otp_code:
            self.is_verified = True
            self.is_active = True
            self.otp_code = None
            self.otp_created_at = None
            self.otp_attempts = 0
            self.save()
            return True, "Email verified successfully!"
        else:
            self.otp_attempts += 1
            self.save()
            return False, f"Invalid OTP. {3 - self.otp_attempts} attempts remaining."
    
    def resend_otp(self):
        """Resend OTP code"""
        # Check if last OTP was sent recently (prevent spam)
        if self.otp_created_at:
            time_since_last = datetime.now() - self.otp_created_at
            if time_since_last.total_seconds() < 60:  # 1 minute cooldown
                remaining = 60 - int(time_since_last.total_seconds())
                return None, f"Please wait {remaining} seconds before requesting a new OTP."
        
        return self.generate_otp(), "OTP sent successfully!"
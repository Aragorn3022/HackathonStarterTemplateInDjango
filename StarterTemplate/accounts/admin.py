from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
from .models import User

# Register your models here.

# Note: Django's default admin is incompatible with MongoEngine users
# because it expects Django ORM models with integer primary keys.
# MongoEngine uses ObjectId strings as primary keys.

class MongoEngineAdminSite(AdminSite):
    """
    Custom admin site that works with MongoEngine users.
    This prevents the ObjectId/integer ID conflict.
    """
    site_header = "MongoEngine Admin"
    site_title = "Admin Portal"
    index_title = "Welcome to MongoEngine Admin"
    
    def has_permission(self, request):
        """
        Check if the user has permission to access the admin.
        MongoEngine users with is_staff=True can access.
        """
        return (
            request.user.is_active and 
            hasattr(request.user, 'is_staff') and 
            request.user.is_staff
        )
    
    def index(self, request, extra_context=None):
        """
        Custom index page for MongoEngine admin.
        """
        if not self.has_permission(request):
            return redirect('login')
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': [],
            'user_count': User.objects.count(),
            'active_users': User.objects(is_active=True).count(),
            'staff_users': User.objects(is_staff=True).count(),
        }
        
        if extra_context:
            context.update(extra_context)
        
        request.current_app = self.name
        
        # Return a simple template response
        return TemplateResponse(
            request, 
            self.index_template or 'admin/index.html',
            context
        )


# Create an instance of our custom admin site
mongoengine_admin_site = MongoEngineAdminSite(name='mongoengine_admin')


# Simple admin class for User model
class UserAdmin:
    """
    Basic admin interface for MongoEngine User model.
    This is a simplified version that doesn't use Django's ModelAdmin.
    """
    model = User
    list_display = ['username', 'email', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email']
    
    def get_queryset(self):
        return User.objects.all()


# Note: We don't register with Django's default admin.site
# Instead, we'll create custom views for managing MongoEngine users

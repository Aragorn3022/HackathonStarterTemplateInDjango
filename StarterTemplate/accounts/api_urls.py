from django.urls import path
from . import api_views

urlpatterns = [
    # Authentication
    path('register/', api_views.api_register, name='api_register'),
    path('login/', api_views.api_login, name='api_login'),
    path('logout/', api_views.api_logout, name='api_logout'),
    
    # User Profile
    path('profile/', api_views.api_profile, name='api_profile'),
    path('profile/update/', api_views.api_update_profile, name='api_update_profile'),
    path('profile/change-password/', api_views.api_change_password, name='api_change_password'),
    path('profile/delete/', api_views.api_delete_account, name='api_delete_account'),
    
    # User List & Detail
    path('users/', api_views.api_user_list, name='api_user_list'),
    path('users/<str:user_id>/', api_views.api_user_detail, name='api_user_detail'),
    
    # Utility
    path('check-username/', api_views.api_check_username, name='api_check_username'),
    path('check-email/', api_views.api_check_email, name='api_check_email'),
]

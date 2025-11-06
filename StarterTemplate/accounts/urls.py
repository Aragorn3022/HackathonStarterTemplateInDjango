from django.urls import path
from . import views, oauth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    
    # OAuth routes
    path('auth/google/', oauth_views.google_login, name='google_login'),
    path('auth/google/callback/', oauth_views.google_callback, name='google_callback'),
]

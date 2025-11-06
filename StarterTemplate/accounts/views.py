from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, UserLoginForm
from .auth_utils import login as auth_login
from .email_utils import send_otp_email, send_welcome_email


def home(request):
    """Home page view"""
    return render(request, 'accounts/home.html')


def user_login(request):
    """Handle user login"""
    if hasattr(request, 'user') and request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Check if user has verified their email
                mongo_user = User.objects(username=username).first()
                if not mongo_user.is_verified:
                    messages.error(request, 'Please verify your email before logging in.')
                    return redirect('login')
                
                auth_login(request, user, backend='accounts.auth_backend.MongoEngineBackend')
                user.update_last_login()
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """Handle user logout"""
    auth_logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile(request):
    """Display user profile"""
    # Fetch the user from MongoDB
    try:
        mongo_user = User.objects.get(id=str(request.user.id))
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')
    
    return render(request, 'accounts/profile.html', {
        'user': mongo_user
    })


def register(request):
    """Handle user registration"""
    if hasattr(request, 'user') and request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user using MongoEngine            username = form.cleaned_data['username']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            
            # Check if user already exists
            if User.objects(username=username).first():
                messages.error(request, 'Username already exists.')
                return render(request, 'accounts/register.html', {'form': form})
            
            if User.objects(email=email).first():
                messages.error(request, 'Email already exists.')
                return render(request, 'accounts/register.html', {'form': form})
              # Create new user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            user.save()
            
            # Generate and send OTP
            otp_code = user.generate_otp()
            print(user.email)
            send_otp_email(user, otp_code)
            
            # Store user_id in session for OTP verification
            request.session['otp_user_id'] = str(user.id)
            
            messages.success(request, 'Account created! Please check your email for the OTP code.')
            return redirect('verify_otp')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def verify_otp(request):
    """Handle OTP verification"""
    user_id = request.session.get('otp_user_id')
    
    if not user_id:
        messages.error(request, 'No pending verification found.')
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('register')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP code.')
            return render(request, 'accounts/verify_otp.html', {'user': user})
        
        # Verify OTP
        success, message = user.verify_otp(otp_code)
        if success:
            # Send welcome email
            send_welcome_email(user, request)
            
            # Clear session
            del request.session['otp_user_id']
            
            # Log the user in
            auth_login(request, user, backend='accounts.auth_backend.MongoEngineBackend')
            messages.success(request, message)
            return redirect('profile')
        else:
            messages.error(request, message)
    
    return render(request, 'accounts/verify_otp.html', {'user': user})


def resend_otp(request):
    """Resend OTP code"""
    user_id = request.session.get('otp_user_id')
    
    if not user_id:
        messages.error(request, 'No pending verification found.')
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id)
        print(user)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('register')
    
    # Resend OTP
    otp_code, message = user.resend_otp()
    print(user.email)
    if otp_code:
        send_otp_email(user, otp_code)
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('verify_otp')


@login_required
def edit_profile(request):
    """Handle profile editing"""
    try:
        user = User.objects.get(id=str(request.user.id))
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')
    
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validate email
        if email and email != user.email:
            if User.objects(email=email).first():
                messages.error(request, 'This email is already in use.')
                return render(request, 'accounts/edit_profile.html', {'user': user})
            user.email = email
        
        # Update basic info
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        
        # Change password if provided
        if new_password:
            if not current_password:
                messages.error(request, 'Please enter your current password.')
                return render(request, 'accounts/edit_profile.html', {'user': user})
            
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return render(request, 'accounts/edit_profile.html', {'user': user})
            
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return render(request, 'accounts/edit_profile.html', {'user': user})
            
            if len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters long.')
                return render(request, 'accounts/edit_profile.html', {'user': user})
            
            user.set_password(new_password)
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'accounts/edit_profile.html', {'user': user})

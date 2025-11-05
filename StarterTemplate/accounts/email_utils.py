"""
Email utility functions for sending OTP and other emails
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_otp_email(user, otp_code):
    """
    Send OTP verification email to user
    """
    subject = 'Verify Your Email - OTP Code'
    
    # Ensure we have a valid from_email
    from_email = settings.DEFAULT_FROM_EMAIL
    if not from_email:
        from_email = 'noreply@example.com'
    
    # HTML email template
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #667eea; margin: 0; }}
            .otp-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px; margin: 30px 0; }}
            .otp-code {{ font-size: 36px; font-weight: bold; letter-spacing: 10px; margin: 20px 0; }}
            .info {{ color: #666; line-height: 1.6; }}
            .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Email Verification</h1>
            </div>
            <p>Hello {user.username},</p>
            <p>Thank you for registering! Please use the following OTP code to verify your email address:</p>
            
            <div class="otp-box">
                <div>Your OTP Code</div>
                <div class="otp-code">{otp_code}</div>
                <div>Valid for 10 minutes</div>
            </div>
            
            <div class="info">
                <p><strong>Important:</strong></p>
                <ul>
                    <li>This code will expire in 10 minutes</li>
                    <li>You have 3 attempts to enter the correct code</li>
                    <li>If you didn't request this code, please ignore this email</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This is an automated email. Please do not reply.</p>
                <p>&copy; 2025 Your Application. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    plain_message = f"""
    Hello {user.username},
    
    Thank you for registering! Please use the following OTP code to verify your email address:
    
    OTP Code: {otp_code}
    
    This code will expire in 10 minutes.
    You have 3 attempts to enter the correct code.
      If you didn't request this code, please ignore this email.
    
    This is an automated email. Please do not reply.
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[user.email],  # Must be a list
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        print(f"Debug info:")
        print(f"  - from_email: {from_email}")
        print(f"  - recipient: {user.email}")
        print(f"  - subject: {subject}")
        import traceback
        traceback.print_exc()
        return False


def send_welcome_email(user):
    """
    Send welcome email after successful verification
    """
    subject = 'Welcome to Our Platform!'
    
    # Ensure we have a valid from_email
    from_email = settings.DEFAULT_FROM_EMAIL
    if not from_email:
        from_email = 'noreply@example.com'
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #667eea; margin: 0; }}
            .content {{ color: #333; line-height: 1.6; }}
            .button {{ display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome Aboard! 🎉</h1>
            </div>
            <div class="content">
                <p>Hello {user.username},</p>
                <p>Your email has been successfully verified! Welcome to our community.</p>
                <p>You can now enjoy all the features of your account:</p>
                <ul>
                    <li>Access your personalized dashboard</li>
                    <li>Update your profile information</li>
                    <li>Connect with other users</li>
                    <li>And much more!</li>
                </ul>
                <p style="text-align: center;">
                    <a href="http://127.0.0.1:8000/profile/" class="button">Go to Your Profile</a>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Your Application. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = f"""
    Hello {user.username},
    
    Your email has been successfully verified! Welcome to our community.
    
    You can now enjoy all the features of your account.
      Visit your profile at: http://127.0.0.1:8000/profile/
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        print(f"Debug info:")
        print(f"  - from_email: {from_email}")
        print(f"  - recipient: {user.email}")
        import traceback
        traceback.print_exc()
        return False

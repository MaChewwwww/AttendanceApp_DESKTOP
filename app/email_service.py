import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import secrets
import string
from datetime import datetime, timedelta
from .config import (
    EMAIL_SMTP_SERVER, 
    EMAIL_SMTP_PORT, 
    EMAIL_ADDRESS, 
    EMAIL_PASSWORD, 
    EMAIL_USE_TLS,
    EMAIL_VERIFICATION_SUBJECT,
    EMAIL_PASSWORD_RESET_SUBJECT,
    APP_NAME
)

class EmailService:
    def __init__(self):
        self.smtp_server = EMAIL_SMTP_SERVER
        self.smtp_port = EMAIL_SMTP_PORT
        self.email = EMAIL_ADDRESS
        self.password = EMAIL_PASSWORD
        self.use_tls = EMAIL_USE_TLS
        
    def _create_smtp_connection(self):
        """Create and return SMTP connection"""
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                # Enable TLS encryption
                context = ssl.create_default_context()
                server.starttls(context=context)
            
            # Login to email account
            server.login(self.email, self.password)
            
            return server
        except Exception as e:
            print(f"Error creating SMTP connection: {e}")
            raise
    
    def send_email(self, to_email, subject, body_text, body_html=None, attachments=None):
        """
        Send an email
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            body_text (str): Plain text body
            body_html (str, optional): HTML body
            attachments (list, optional): List of file paths to attach
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Validate email configuration
            if not self.email or not self.password:
                return False, "Email credentials not configured"
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email
            message["To"] = to_email
            
            # Add text part
            text_part = MIMEText(body_text, "plain")
            message.attach(text_part)
            
            # Add HTML part if provided
            if body_html:
                html_part = MIMEText(body_html, "html")
                message.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {file_path.split('/')[-1]}"
                        )
                        message.attach(part)
                    except Exception as e:
                        print(f"Error attaching file {file_path}: {e}")
            
            # Send email
            server = self._create_smtp_connection()
            text = message.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def generate_verification_token(self, length=32):
        """Generate a secure random token for email verification"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def send_verification_email(self, to_email, first_name, verification_token):
        """
        Send email verification email
        
        Args:
            to_email (str): Recipient email
            first_name (str): User's first name
            verification_token (str): Verification token
            
        Returns:
            tuple: (success, message)
        """
        try:
            subject = EMAIL_VERIFICATION_SUBJECT
            
            # Create verification URL (you'll need to implement this endpoint)
            verification_url = f"http://localhost:8000/verify-email?token={verification_token}"
            
            # Plain text version
            body_text = f"""
Hello {first_name},

Welcome to {APP_NAME}!

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
{APP_NAME} Team
            """.strip()
            
            # HTML version
            body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #1E3A8A; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #1E3A8A; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{APP_NAME}</h1>
        </div>
        <div class="content">
            <h2>Welcome, {first_name}!</h2>
            <p>Thank you for registering with {APP_NAME}. To complete your registration, please verify your email address.</p>
            <p>
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p><a href="{verification_url}">{verification_url}</a></p>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p>If you didn't create an account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 {APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_email, subject, body_text, body_html)
            
        except Exception as e:
            error_msg = f"Failed to send verification email: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def send_password_reset_email(self, to_email, first_name, reset_token):
        """
        Send password reset email
        
        Args:
            to_email (str): Recipient email
            first_name (str): User's first name
            reset_token (str): Password reset token
            
        Returns:
            tuple: (success, message)
        """
        try:
            subject = EMAIL_PASSWORD_RESET_SUBJECT
            
            # Create reset URL (you'll need to implement this endpoint)
            reset_url = f"http://localhost:8000/reset-password?token={reset_token}"
            
            # Plain text version
            body_text = f"""
Hello {first_name},

You have requested to reset your password for {APP_NAME}.

Please click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email.

Best regards,
{APP_NAME} Team
            """.strip()
            
            # HTML version
            body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #dc2626; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{APP_NAME}</h1>
        </div>
        <div class="content">
            <h2>Password Reset Request</h2>
            <p>Hello {first_name},</p>
            <p>You have requested to reset your password for {APP_NAME}.</p>
            <p>
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p><strong>This link will expire in 1 hour.</strong></p>
            <p>If you didn't request this reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 {APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_email, subject, body_text, body_html)
            
        except Exception as e:
            error_msg = f"Failed to send password reset email: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def send_welcome_email(self, to_email, first_name):
        """
        Send welcome email after successful verification
        
        Args:
            to_email (str): Recipient email
            first_name (str): User's first name
            
        Returns:
            tuple: (success, message)
        """
        try:
            subject = f"Welcome to {APP_NAME}!"
            
            # Plain text version
            body_text = f"""
Hello {first_name},

Welcome to {APP_NAME}! Your account has been successfully verified.

You can now:
- Submit attendance using face recognition
- View your attendance history
- Track your attendance analytics

Thank you for joining us!

Best regards,
{APP_NAME} Team
            """.strip()
            
            # HTML version
            body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #10B981; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .feature {{ padding: 10px; margin: 10px 0; background-color: white; border-radius: 5px; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to {APP_NAME}!</h1>
        </div>
        <div class="content">
            <h2>Hello {first_name},</h2>
            <p>Congratulations! Your account has been successfully verified and is now active.</p>
            
            <h3>What you can do now:</h3>
            <div class="feature">
                <strong>📸 Face Recognition Attendance</strong><br>
                Submit your attendance quickly and securely using face recognition technology.
            </div>
            <div class="feature">
                <strong>📊 Attendance History</strong><br>
                View and track your attendance records over time.
            </div>
            <div class="feature">
                <strong>📈 Analytics Dashboard</strong><br>
                Get insights into your attendance patterns and performance.
            </div>
            
            <p>Thank you for choosing {APP_NAME}. We're excited to have you on board!</p>
        </div>
        <div class="footer">
            <p>© 2024 {APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_email, subject, body_text, body_html)
            
        except Exception as e:
            error_msg = f"Failed to send welcome email: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def test_email_configuration(self):
        """
        Test email configuration by sending a test email to the configured email address
        
        Returns:
            tuple: (success, message)
        """
        try:
            if not self.email:
                return False, "No email address configured"
                
            subject = f"{APP_NAME} - Email Configuration Test"
            body_text = f"""
This is a test email to verify that your email configuration is working correctly.

If you received this email, your {APP_NAME} email service is configured properly.

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            return self.send_email(self.email, subject, body_text)
            
        except Exception as e:
            error_msg = f"Email configuration test failed: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def send_login_otp_email(self, to_email, first_name, otp_code):
        """
        Send login OTP email
        
        Args:
            to_email (str): Recipient email
            first_name (str): User's first name
            otp_code (str): 6-digit OTP code
            
        Returns:
            tuple: (success, message)
        """
        try:
            subject = f"{APP_NAME} - Login OTP"
            
            # Plain text version
            body_text = f"""
Hello {first_name},

Your login OTP code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
{APP_NAME} Team
            """.strip()
            
            # HTML version
            body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #1E3A8A; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .otp-code {{ 
            display: inline-block; 
            padding: 15px 25px; 
            background-color: #f0f9ff; 
            border: 2px solid #1E3A8A;
            color: #1E3A8A; 
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 3px;
            border-radius: 8px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{APP_NAME}</h1>
        </div>
        <div class="content">
            <h2>Login OTP Code</h2>
            <p>Hello {first_name},</p>
            <p>Your login verification code is:</p>
            <div style="text-align: center;">
                <span class="otp-code">{otp_code}</span>
            </div>
            <p><strong>This code will expire in 10 minutes.</strong></p>
            <p>If you didn't request this code, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 {APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_email, subject, body_text, body_html)
            
        except Exception as e:
            error_msg = f"Failed to send login OTP email: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def send_password_reset_otp_email(self, to_email, first_name, otp_code):
        """
        Send password reset OTP email
        
        Args:
            to_email (str): Recipient email
            first_name (str): User's first name
            otp_code (str): 6-digit OTP code
            
        Returns:
            tuple: (success, message)
        """
        try:
            subject = f"{APP_NAME} - Password Reset OTP"
            
            # Plain text version
            body_text = f"""
Hello {first_name},

Your password reset OTP code is: {otp_code}

This code will expire in 15 minutes.

If you didn't request this password reset, please ignore this email.

Best regards,
{APP_NAME} Team
            """.strip()
            
            # HTML version
            body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .otp-code {{ 
            display: inline-block; 
            padding: 15px 25px; 
            background-color: #fef2f2; 
            border: 2px solid #dc2626;
            color: #dc2626; 
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 3px;
            border-radius: 8px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{APP_NAME}</h1>
        </div>
        <div class="content">
            <h2>Password Reset OTP</h2>
            <p>Hello {first_name},</p>
            <p>Your password reset verification code is:</p>
            <div style="text-align: center;">
                <span class="otp-code">{otp_code}</span>
            </div>
            <p><strong>This code will expire in 15 minutes.</strong></p>
            <p>If you didn't request this password reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 {APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_email, subject, body_text, body_html)
            
        except Exception as e:
            error_msg = f"Failed to send password reset OTP email: {str(e)}"
            print(error_msg)
            return False, error_msg

    def send_registration_confirmation_email(self, to_email, first_name):
        """
        Send registration confirmation email (not welcome - user is pending approval)
        
        Args:
            to_email (str): Recipient email
            first_name (str): User's first name
            
        Returns:
            tuple: (success, message)
        """
        try:
            subject = f"{APP_NAME} - Registration Received"
            
            # Plain text version
            body_text = f"""
Hello {first_name},

Thank you for registering with {APP_NAME}!

Your registration has been received and is currently being reviewed by our administrators.

What happens next:
- Your account will be verified within 1-3 business days
- You will receive an email notification when your account is approved
- Once approved, you can log in using your credentials

If you have any questions, please contact our support team.

Best regards,
{APP_NAME} Team
            """.strip()
            
            # HTML version
            body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f59e0b; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .step {{ padding: 10px; margin: 10px 0; background-color: white; border-radius: 5px; border-left: 4px solid #f59e0b; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{APP_NAME}</h1>
            <h2>Registration Received</h2>
        </div>
        <div class="content">
            <h2>Hello {first_name},</h2>
            <p>Thank you for registering with {APP_NAME}! Your registration has been received and is currently being reviewed.</p>
            
            <h3>What happens next:</h3>
            <div class="step">
                <strong>📋 Review Process</strong><br>
                Your account will be verified within 1-3 business days by our administrators.
            </div>
            <div class="step">
                <strong>📧 Email Notification</strong><br>
                You will receive an email notification when your account is approved.
            </div>
            <div class="step">
                <strong>🚀 Access Granted</strong><br>
                Once approved, you can log in using your credentials and access all features.
            </div>
            
            <p>If you have any questions during this process, please contact our support team.</p>
        </div>
        <div class="footer">
            <p>© 2024 {APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_email, subject, body_text, body_html)
            
        except Exception as e:
            error_msg = f"Failed to send registration confirmation email: {str(e)}"
            print(error_msg)
            return False, error_msg

    def send_registration_otp_email(self, to_email, first_name, otp_code):
        """
        Send registration OTP email
        
        Args:
            to_email (str): Recipient email
            first_name (str): User's first name
            otp_code (str): 6-digit OTP code
            
        Returns:
            tuple: (success, message)
        """
        try:
            subject = f"{APP_NAME} - Registration Verification"
            
            # Plain text version
            body_text = f"""
Hello {first_name},

Your registration verification code is: {otp_code}

This code will expire in 15 minutes.

If you didn't request this registration, please ignore this email.

Best regards,
{APP_NAME} Team
            """.strip()
            
            # HTML version
            body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #10B981; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .otp-code {{ 
            display: inline-block; 
            padding: 15px 25px; 
            background-color: #f0fdf4; 
            border: 2px solid #10B981;
            color: #10B981; 
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 3px;
            border-radius: 8px; 
            margin: 20px 0;
        }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{APP_NAME}</h1>
            <h2>Registration Verification</h2>
        </div>
        <div class="content">
            <h2>Almost Done!</h2>
            <p>Hello {first_name},</p>
            <p>To complete your registration, please enter this verification code:</p>
            <div style="text-align: center;">
                <span class="otp-code">{otp_code}</span>
            </div>
            <p><strong>This code will expire in 15 minutes.</strong></p>
            <p>If you didn't request this registration, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 {APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_email, subject, body_text, body_html)
            
        except Exception as e:
            error_msg = f"Failed to send registration OTP email: {str(e)}"
            print(error_msg)
            return False, error_msg

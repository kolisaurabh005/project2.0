"""
Email Service for sending OTP and notification emails.
Uses Flask-Mail with Gmail SMTP configuration.
"""

from flask import current_app
from flask_mail import Message


class EmailService:
    """Service for sending emails via Flask-Mail."""
    
    # Email instance will be set by the app
    mail = None
    
    @classmethod
    def init_app(cls, mail_instance):
        """
        Initialize with Flask-Mail instance.
        
        Args:
            mail_instance: Flask-Mail instance from app
        """
        cls.mail = mail_instance
    
    @classmethod
    def send_otp_email(cls, to_email: str, otp: str, purpose: str = 'verification') -> bool:
        """
        Send OTP email to user.
        
        Args:
            to_email: Recipient email address
            otp: The OTP code to send
            purpose: Purpose of OTP ('login', 'language_change', etc.)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if cls.mail is None:
                print(f"[EMAIL SIMULATION] OTP for {to_email}: {otp}")
                return True
            
            subject = f"Your OTP for {purpose.replace('_', ' ').title()}"
            
            # Create email body
            body = f"""
Hello,

Your One-Time Password (OTP) for {purpose.replace('_', ' ')} is:

    {otp}

This OTP is valid for {current_app.config.get('OTP_EXPIRY_MINUTES', 5)} minutes.

If you did not request this OTP, please ignore this email.

Regards,
Secure Multi-Language App Team
            """
            
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .otp-box {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            letter-spacing: 8px;
            margin: 20px 0;
        }}
        .footer {{ font-size: 12px; color: #666; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Your OTP for {purpose.replace('_', ' ').title()}</h2>
        <p>Hello,</p>
        <p>Your One-Time Password (OTP) is:</p>
        <div class="otp-box">{otp}</div>
        <p>This OTP is valid for <strong>{current_app.config.get('OTP_EXPIRY_MINUTES', 5)} minutes</strong>.</p>
        <p>If you did not request this OTP, please ignore this email.</p>
        <div class="footer">
            <p>Regards,<br>Secure Multi-Language App Team</p>
        </div>
    </div>
</body>
</html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[to_email],
                body=body,
                html=html_body
            )
            
            cls.mail.send(msg)
            print(f"[EMAIL SENT] OTP email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email to {to_email}: {str(e)}")
            # Fallback to simulation if email fails
            print(f"[EMAIL SIMULATION] OTP for {to_email}: {otp}")
            return False
    
    @classmethod
    def send_login_alert(cls, to_email: str, login_info: dict) -> bool:
        """
        Send login notification email.
        
        Args:
            to_email: Recipient email address
            login_info: Dictionary with browser, os, ip, time
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if cls.mail is None:
                print(f"[EMAIL SIMULATION] Login alert for {to_email}")
                return True
            
            subject = "New Login Detected"
            
            body = f"""
Hello,

A new login was detected on your account:

Browser: {login_info.get('browser', 'Unknown')}
Operating System: {login_info.get('os', 'Unknown')}
Device Type: {login_info.get('device_type', 'Unknown')}
IP Address: {login_info.get('ip', 'Unknown')}
Time: {login_info.get('time', 'Unknown')}

If this wasn't you, please secure your account immediately.

Regards,
Secure Multi-Language App Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[to_email],
                body=body
            )
            
            cls.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send login alert: {str(e)}")
            return False

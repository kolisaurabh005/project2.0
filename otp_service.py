"""
OTP Service for generating and validating one-time passwords.
Supports both email and mobile (simulated) OTP with session-based storage.
"""

import random
import string
from datetime import datetime, timedelta
from flask import session, current_app


class OTPService:
    """Service for OTP generation, storage, and validation."""
    
    # Session keys for different OTP purposes
    OTP_KEY_LOGIN = 'login_otp'
    OTP_KEY_LANGUAGE = 'language_otp'
    
    @staticmethod
    def generate_otp(length: int = None) -> str:
        """
        Generate a random numeric OTP.
        
        Args:
            length: Length of OTP (default from config)
            
        Returns:
            Generated OTP string
        """
        if length is None:
            length = current_app.config.get('OTP_LENGTH', 6)
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def store_otp(otp: str, purpose: str, otp_type: str, target: str = None):
        """
        Store OTP in session with expiry time.
        
        Args:
            otp: The OTP to store
            purpose: Purpose of OTP ('login' or 'language')
            otp_type: Type of OTP ('email' or 'mobile')
            target: Email or mobile number (optional, for logging)
        """
        expiry_minutes = current_app.config.get('OTP_EXPIRY_MINUTES', 5)
        expiry_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        session_key = f'{purpose}_otp_data'
        session[session_key] = {
            'otp': otp,
            'type': otp_type,
            'target': target,
            'expiry': expiry_time.isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def validate_otp(entered_otp: str, purpose: str) -> dict:
        """
        Validate OTP entered by user.
        
        Args:
            entered_otp: OTP entered by user
            purpose: Purpose of OTP ('login' or 'language')
            
        Returns:
            Dictionary with 'valid' (bool), 'message' (str), and 'type' (str)
        """
        session_key = f'{purpose}_otp_data'
        otp_data = session.get(session_key)
        
        if not otp_data:
            return {
                'valid': False,
                'message': 'No OTP found. Please request a new OTP.',
                'type': None
            }
        
        # Check expiry
        expiry_time = datetime.fromisoformat(otp_data['expiry'])
        if datetime.utcnow() > expiry_time:
            # Clear expired OTP
            OTPService.clear_otp(purpose)
            return {
                'valid': False,
                'message': 'OTP has expired. Please request a new OTP.',
                'type': otp_data['type']
            }
        
        # Validate OTP
        if str(entered_otp) == str(otp_data['otp']):
            otp_type = otp_data['type']
            # Clear OTP after successful validation
            OTPService.clear_otp(purpose)
            return {
                'valid': True,
                'message': 'OTP verified successfully.',
                'type': otp_type
            }
        
        return {
            'valid': False,
            'message': 'Invalid OTP. Please try again.',
            'type': otp_data['type']
        }
    
    @staticmethod
    def clear_otp(purpose: str):
        """
        Clear OTP from session.
        
        Args:
            purpose: Purpose of OTP to clear ('login' or 'language')
        """
        session_key = f'{purpose}_otp_data'
        session.pop(session_key, None)
    
    @staticmethod
    def get_otp_info(purpose: str) -> dict:
        """
        Get information about stored OTP (without revealing the OTP itself).
        
        Args:
            purpose: Purpose of OTP ('login' or 'language')
            
        Returns:
            Dictionary with OTP info or None if not found
        """
        session_key = f'{purpose}_otp_data'
        otp_data = session.get(session_key)
        
        if not otp_data:
            return None
        
        expiry_time = datetime.fromisoformat(otp_data['expiry'])
        remaining_seconds = (expiry_time - datetime.utcnow()).total_seconds()
        
        return {
            'type': otp_data['type'],
            'target': otp_data.get('target', 'Unknown'),
            'remaining_seconds': max(0, int(remaining_seconds)),
            'is_expired': remaining_seconds <= 0
        }
    
    @staticmethod
    def generate_and_store_email_otp(email: str, purpose: str) -> str:
        """
        Generate OTP for email verification and store it.
        
        Args:
            email: User's email address
            purpose: Purpose of OTP ('login' or 'language')
            
        Returns:
            Generated OTP
        """
        otp = OTPService.generate_otp()
        OTPService.store_otp(otp, purpose, 'email', email)
        return otp
    
    @staticmethod
    def generate_and_store_mobile_otp(mobile: str, purpose: str) -> str:
        """
        Generate OTP for mobile verification and store it (simulated).
        
        Args:
            mobile: User's mobile number
            purpose: Purpose of OTP ('login' or 'language')
            
        Returns:
            Generated OTP
        """
        otp = OTPService.generate_otp()
        OTPService.store_otp(otp, purpose, 'mobile', mobile)
        # Log OTP to console for simulation
        print(f"[SIMULATED MOBILE OTP] Sending OTP {otp} to {mobile}")
        return otp

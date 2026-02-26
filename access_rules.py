"""
Access Rules Service for implementing browser and device-based access restrictions.

Rules:
1. Chrome: Email OTP verification required
2. Edge: Direct access allowed (no OTP)
3. Mobile: Access only between 10:00 AM and 1:00 PM
"""

from datetime import datetime
from flask import current_app
import pytz


class AccessRules:
    """Service for enforcing browser and device-based access rules."""
    
    # Access rule types
    RULE_ALLOW = 'allow'           # Direct access allowed
    RULE_OTP_EMAIL = 'otp_email'   # Email OTP required
    RULE_OTP_MOBILE = 'otp_mobile' # Mobile OTP required
    RULE_DENY = 'deny'             # Access denied
    
    @staticmethod
    def get_current_hour(timezone: str = 'UTC') -> int:
        """
        Get current hour in specified timezone.
        
        Args:
            timezone: Timezone name (default UTC)
            
        Returns:
            Current hour (0-23)
        """
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
        except Exception:
            current_time = datetime.utcnow()
        
        return current_time.hour
    
    @staticmethod
    def is_within_mobile_access_hours(timezone: str = 'Asia/Kolkata') -> bool:
        """
        Check if current time is within mobile access hours (10 AM - 1 PM).
        
        Args:
            timezone: Timezone for checking (default India timezone)
            
        Returns:
            True if within allowed hours, False otherwise
        """
        start_hour = current_app.config.get('MOBILE_ACCESS_START_HOUR', 10)
        end_hour = current_app.config.get('MOBILE_ACCESS_END_HOUR', 13)
        
        current_hour = AccessRules.get_current_hour(timezone)
        return start_hour <= current_hour < end_hour
    
    @staticmethod
    def check_login_access(browser_family: str, is_mobile: bool, timezone: str = 'Asia/Kolkata') -> dict:
        """
        Determine access rule based on browser and device type.
        
        Rules:
        1. Chrome browser: Require email OTP
        2. Edge browser: Allow direct access
        3. Mobile device: Allow only 10 AM - 1 PM, deny otherwise
        4. Other browsers: Allow direct access (default)
        
        Args:
            browser_family: Browser name (e.g., 'Chrome', 'Edge', 'Firefox')
            is_mobile: Whether device is mobile
            timezone: Timezone for time checks
            
        Returns:
            Dictionary with:
            - rule: Access rule type (allow, otp_email, otp_mobile, deny)
            - message: Human-readable message
            - allowed_hours: For mobile denial, shows allowed time range
        """
        browser_lower = browser_family.lower() if browser_family else ''
        
        # Rule 3: Mobile device time restriction (check this first)
        mobile_allowed = True
        mobile_msg = ""
        
        if is_mobile:
            if not AccessRules.is_within_mobile_access_hours(timezone):
                start_hour = current_app.config.get('MOBILE_ACCESS_START_HOUR', 10)
                end_hour = current_app.config.get('MOBILE_ACCESS_END_HOUR', 13)
                return {
                    'rule': AccessRules.RULE_DENY,
                    'message': f'Mobile access is only allowed between {start_hour}:00 AM and {end_hour % 12}:00 PM.',
                    'allowed_hours': f'{start_hour}:00 AM - {end_hour % 12}:00 PM'
                }
            else:
                mobile_allowed = True
                mobile_msg = "Mobile access allowed during permitted hours. "
        
        # Rule 1: Chrome requires email OTP
        if 'chrome' in browser_lower and 'edge' not in browser_lower:
            return {
                'rule': AccessRules.RULE_OTP_EMAIL,
                'message': mobile_msg + 'Chrome browser detected. Email OTP verification required.',
                'allowed_hours': None
            }
        
        # Rule 2: Edge allows direct access
        if 'edge' in browser_lower:
            return {
                'rule': AccessRules.RULE_ALLOW,
                'message': mobile_msg + 'Edge browser detected. Access granted.',
                'allowed_hours': None
            }
        
        # Default: Allow access for other browsers
        return {
            'rule': AccessRules.RULE_ALLOW,
            'message': mobile_msg + 'Access granted.',
            'allowed_hours': None
        }
    
    @staticmethod
    def get_language_change_rule(language: str) -> dict:
        """
        Determine OTP rule for language change.
        
        Rules:
        - French (fr): Email OTP required
        - All other languages: Mobile OTP required
        
        Args:
            language: Language code (en, hi, es, pt, zh, fr)
            
        Returns:
            Dictionary with rule type and message
        """
        if language.lower() == 'fr':
            return {
                'rule': AccessRules.RULE_OTP_EMAIL,
                'message': 'French language requires email OTP verification.',
                'otp_type': 'email'
            }
        else:
            return {
                'rule': AccessRules.RULE_OTP_MOBILE,
                'message': f'Language change to {language.upper()} requires mobile OTP verification.',
                'otp_type': 'mobile'
            }
    
    @staticmethod
    def format_access_denial_message(rule_result: dict, language_code: str = 'en') -> str:
        """
        Format access denial message for display.
        
        Args:
            rule_result: Result from check_login_access
            language_code: Language for message (for future i18n)
            
        Returns:
            Formatted message string
        """
        if rule_result['rule'] == AccessRules.RULE_DENY:
            return rule_result['message']
        return ''

"""
Authentication Routes Blueprint.
Handles user registration, login, logout, and session management.
Implements browser-based access rules.
"""

from flask import Blueprint, request, jsonify, session
from models import User, LoginHistory
from services import DeviceService, AccessRules, OTPService, EmailService
import sqlite3

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Expected JSON body:
    {
        "name": "User Name",
        "email": "user@example.com",
        "password": "securepassword",
        "mobile": "1234567890"
    }
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'password', 'mobile']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': f'{field.capitalize()} is required.'
            }), 400
    
    # Validate email format (basic check)
    if '@' not in data['email'] or '.' not in data['email']:
        return jsonify({
            'success': False,
            'message': 'Invalid email format.'
        }), 400
    
    # Validate password length
    if len(data['password']) < 6:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 6 characters.'
        }), 400
    
    try:
        # Create user
        user_id = User.create(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            mobile=data['mobile']
        )
        
        return jsonify({
            'success': True,
            'message': 'Registration successful. Please login.',
            'user_id': user_id
        }), 201
        
    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'message': 'Email already registered.'
        }), 409


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user with browser/device-based access rules.
    
    Expected JSON body:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    
    Returns:
    - For Chrome: Requires OTP verification (returns otp_required: true)
    - For Edge: Direct login (returns success with user data)
    - For Mobile: Checks time restriction (10 AM - 1 PM)
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': 'Email and password are required.'
        }), 400
    
    # Verify credentials
    user = User.verify_password(data['email'], data['password'])
    if not user:
        return jsonify({
            'success': False,
            'message': 'Invalid email or password.'
        }), 401
    
    # Get device information
    device_info = DeviceService.get_device_info()
    
    # Check access rules based on browser/device
    access_result = AccessRules.check_login_access(
        browser_family=device_info.get('browser_family', ''),
        is_mobile=device_info.get('is_mobile', False)
    )
    
    # Handle access denial (mobile time restriction)
    if access_result['rule'] == AccessRules.RULE_DENY:
        return jsonify({
            'success': False,
            'message': access_result['message'],
            'access_denied': True,
            'allowed_hours': access_result.get('allowed_hours')
        }), 403
    
    # Handle OTP requirement (Chrome browser)
    if access_result['rule'] == AccessRules.RULE_OTP_EMAIL:
        # Store pending login data in session
        session['pending_login'] = {
            'user_id': user['id'],
            'email': user['email'],
            'device_info': device_info
        }
        
        # Generate and send OTP
        otp = OTPService.generate_and_store_email_otp(user['email'], 'login')
        EmailService.send_otp_email(user['email'], otp, 'login')
        
        return jsonify({
            'success': True,
            'otp_required': True,
            'otp_type': 'email',
            'message': access_result['message'],
            'email_hint': f"OTP sent to {user['email'][:3]}***{user['email'].split('@')[1]}"
        }), 200
    
    # Direct login allowed (Edge or other browsers)
    return complete_login(user, device_info)


@auth_bp.route('/verify-login-otp', methods=['POST'])
def verify_login_otp():
    """
    Verify OTP for Chrome browser login.
    
    Expected JSON body:
    {
        "otp": "123456"
    }
    """
    data = request.get_json()
    
    if not data.get('otp'):
        return jsonify({
            'success': False,
            'message': 'OTP is required.'
        }), 400
    
    # Check if there's a pending login
    pending_login = session.get('pending_login')
    if not pending_login:
        return jsonify({
            'success': False,
            'message': 'No pending login found. Please start login again.'
        }), 400
    
    # Validate OTP
    otp_result = OTPService.validate_otp(data['otp'], 'login')
    
    if not otp_result['valid']:
        return jsonify({
            'success': False,
            'message': otp_result['message']
        }), 400
    
    # OTP valid - complete login
    user = User.get_by_id(pending_login['user_id'])
    if not user:
        session.pop('pending_login', None)
        return jsonify({
            'success': False,
            'message': 'User not found.'
        }), 404
    
    device_info = pending_login['device_info']
    session.pop('pending_login', None)
    
    return complete_login(user, device_info)


def complete_login(user: dict, device_info: dict):
    """
    Complete the login process after all verifications pass.
    Records login history and sets up session.
    """
    # Record login history
    LoginHistory.create(
        user_id=user['id'],
        ip_address=device_info.get('ip_address', '127.0.0.1'),
        browser=device_info.get('browser', 'Unknown'),
        os=device_info.get('os', 'Unknown'),
        device_type=device_info.get('device_type', 'desktop')
    )
    
    # Set up session
    session['user_id'] = user['id']
    session['user_email'] = user['email']
    session['user_name'] = user['name']
    session['logged_in'] = True
    
    # Return user data (excluding password)
    user_data = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify({
        'success': True,
        'message': 'Login successful.',
        'user': user_data,
        'device_info': {
            'browser': device_info.get('browser'),
            'os': device_info.get('os'),
            'device_type': device_info.get('device_type')
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user and clear session.
    """
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logout successful.'
    }), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current logged-in user's information.
    """
    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'message': 'Not authenticated.',
            'authenticated': False
        }), 401
    
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({
            'success': False,
            'message': 'User not found.',
            'authenticated': False
        }), 404
    
    # Return user data (excluding password)
    user_data = {k: v for k, v in user.items() if k != 'password'}
    
    return jsonify({
        'success': True,
        'authenticated': True,
        'user': user_data
    }), 200


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP for pending login.
    """
    pending_login = session.get('pending_login')
    if not pending_login:
        return jsonify({
            'success': False,
            'message': 'No pending login found.'
        }), 400
    
    # Generate and send new OTP
    otp = OTPService.generate_and_store_email_otp(pending_login['email'], 'login')
    EmailService.send_otp_email(pending_login['email'], otp, 'login')
    
    return jsonify({
        'success': True,
        'message': 'OTP resent successfully.',
        'email_hint': f"OTP sent to {pending_login['email'][:3]}***{pending_login['email'].split('@')[1]}"
    }), 200

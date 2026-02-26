"""
Language Routes Blueprint.
Handles multilingual functionality with OTP verification for language changes.

Rules:
- French (fr): Email OTP required
- All other languages: Mobile OTP required
"""

from flask import Blueprint, request, jsonify, session, current_app
import os
import json
from models import User, LanguageLog
from services import OTPService, EmailService, AccessRules
from functools import wraps

language_bp = Blueprint('language', __name__, url_prefix='/api/language')


def login_required(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({
                'success': False,
                'message': 'Authentication required.',
                'authenticated': False
            }), 401
        return f(*args, **kwargs)
    return decorated_function


@language_bp.route('/translations/<lang_code>', methods=['GET'])
def get_translations(lang_code):
    """
    Get translations for a specific language.
    Available languages: en, hi, es, pt, zh, fr
    """
    supported_languages = current_app.config.get('SUPPORTED_LANGUAGES', 
                                                   ['en', 'hi', 'es', 'pt', 'zh', 'fr'])
    
    if lang_code not in supported_languages:
        return jsonify({
            'success': False,
            'message': f'Language {lang_code} not supported.',
            'supported_languages': supported_languages
        }), 400
    
    # Load translation file
    translations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations')
    translation_file = os.path.join(translations_dir, f'{lang_code}.json')
    
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        return jsonify({
            'success': True,
            'language': lang_code,
            'translations': translations
        }), 200
        
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'message': f'Translation file for {lang_code} not found.'
        }), 404
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'message': f'Invalid translation file for {lang_code}.'
        }), 500


@language_bp.route('/available', methods=['GET'])
def get_available_languages():
    """
    Get list of available languages with their names.
    """
    languages = [
        {'code': 'en', 'name': 'English', 'native_name': 'English'},
        {'code': 'hi', 'name': 'Hindi', 'native_name': 'हिन्दी'},
        {'code': 'es', 'name': 'Spanish', 'native_name': 'Español'},
        {'code': 'pt', 'name': 'Portuguese', 'native_name': 'Português'},
        {'code': 'zh', 'name': 'Chinese', 'native_name': '中文'},
        {'code': 'fr', 'name': 'French', 'native_name': 'Français'}
    ]
    
    return jsonify({
        'success': True,
        'languages': languages
    }), 200


@language_bp.route('/current', methods=['GET'])
@login_required
def get_current_language():
    """
    Get user's current language preference.
    """
    user_id = session['user_id']
    current_lang = LanguageLog.get_current_language(user_id)
    
    return jsonify({
        'success': True,
        'current_language': current_lang
    }), 200


@language_bp.route('/change', methods=['POST'])
@login_required
def initiate_language_change():
    """
    Initiate language change with OTP verification.
    
    Expected JSON body:
    {
        "language": "fr"  // Target language code
    }
    
    Rules:
    - French (fr): Email OTP required
    - Other languages: Mobile OTP required
    """
    data = request.get_json()
    target_language = data.get('language', '').lower()
    
    # Validate language
    supported_languages = current_app.config.get('SUPPORTED_LANGUAGES',
                                                   ['en', 'hi', 'es', 'pt', 'zh', 'fr'])
    
    if target_language not in supported_languages:
        return jsonify({
            'success': False,
            'message': f'Language {target_language} not supported.',
            'supported_languages': supported_languages
        }), 400
    
    # Check if already using this language
    user_id = session['user_id']
    current_lang = LanguageLog.get_current_language(user_id)
    
    if target_language == current_lang:
        return jsonify({
            'success': False,
            'message': 'You are already using this language.'
        }), 400
    
    # Get user info
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found.'
        }), 404
    
    # Determine OTP type based on language
    rule = AccessRules.get_language_change_rule(target_language)
    
    # Store pending language change
    session['pending_language_change'] = {
        'target_language': target_language,
        'otp_type': rule['otp_type']
    }
    
    # Generate and send OTP
    if rule['otp_type'] == 'email':
        otp = OTPService.generate_and_store_email_otp(user['email'], 'language')
        EmailService.send_otp_email(user['email'], otp, 'language_change')
        target_hint = f"{user['email'][:3]}***@{user['email'].split('@')[1]}"
    else:  # mobile
        otp = OTPService.generate_and_store_mobile_otp(user['mobile'], 'language')
        target_hint = f"******{user['mobile'][-4:]}" if len(user['mobile']) > 4 else '***'
    
    return jsonify({
        'success': True,
        'otp_required': True,
        'otp_type': rule['otp_type'],
        'message': rule['message'],
        'target_hint': target_hint,
        'target_language': target_language
    }), 200


@language_bp.route('/verify-change', methods=['POST'])
@login_required
def verify_language_change():
    """
    Verify OTP and complete language change.
    
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
    
    # Check pending language change
    pending = session.get('pending_language_change')
    if not pending:
        return jsonify({
            'success': False,
            'message': 'No pending language change found. Please initiate change again.'
        }), 400
    
    # Validate OTP
    otp_result = OTPService.validate_otp(data['otp'], 'language')
    
    if not otp_result['valid']:
        return jsonify({
            'success': False,
            'message': otp_result['message']
        }), 400
    
    # OTP valid - complete language change
    user_id = session['user_id']
    target_language = pending['target_language']
    verified_by = pending['otp_type']
    
    # Log language change
    LanguageLog.create(user_id, target_language, verified_by)
    
    # Clear pending change
    session.pop('pending_language_change', None)
    
    return jsonify({
        'success': True,
        'message': f'Language changed to {target_language.upper()} successfully.',
        'new_language': target_language,
        'verified_by': verified_by
    }), 200


@language_bp.route('/resend-otp', methods=['POST'])
@login_required
def resend_language_otp():
    """
    Resend OTP for pending language change.
    """
    pending = session.get('pending_language_change')
    if not pending:
        return jsonify({
            'success': False,
            'message': 'No pending language change found.'
        }), 400
    
    user = User.get_by_id(session['user_id'])
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found.'
        }), 404
    
    # Generate and send new OTP
    if pending['otp_type'] == 'email':
        otp = OTPService.generate_and_store_email_otp(user['email'], 'language')
        EmailService.send_otp_email(user['email'], otp, 'language_change')
        target_hint = f"{user['email'][:3]}***@{user['email'].split('@')[1]}"
    else:
        otp = OTPService.generate_and_store_mobile_otp(user['mobile'], 'language')
        target_hint = f"******{user['mobile'][-4:]}" if len(user['mobile']) > 4 else '***'
    
    return jsonify({
        'success': True,
        'message': 'OTP resent successfully.',
        'otp_type': pending['otp_type'],
        'target_hint': target_hint
    }), 200


@language_bp.route('/cancel-change', methods=['POST'])
@login_required
def cancel_language_change():
    """
    Cancel pending language change.
    """
    session.pop('pending_language_change', None)
    OTPService.clear_otp('language')
    
    return jsonify({
        'success': True,
        'message': 'Language change cancelled.'
    }), 200

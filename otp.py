"""
OTP Routes Blueprint.
Provides endpoints for OTP status and validation.
"""

from flask import Blueprint, request, jsonify, session
from services import OTPService

otp_bp = Blueprint('otp', __name__, url_prefix='/api/otp')


@otp_bp.route('/status/<purpose>', methods=['GET'])
def get_otp_status(purpose):
    """
    Get status of current OTP (if any) for a given purpose.
    
    Args:
        purpose: 'login' or 'language'
    """
    if purpose not in ['login', 'language']:
        return jsonify({
            'success': False,
            'message': 'Invalid OTP purpose.'
        }), 400
    
    otp_info = OTPService.get_otp_info(purpose)
    
    if not otp_info:
        return jsonify({
            'success': True,
            'has_otp': False,
            'message': 'No active OTP found.'
        }), 200
    
    return jsonify({
        'success': True,
        'has_otp': True,
        'otp_type': otp_info['type'],
        'target_hint': mask_target(otp_info['target'], otp_info['type']),
        'remaining_seconds': otp_info['remaining_seconds'],
        'is_expired': otp_info['is_expired']
    }), 200


@otp_bp.route('/validate', methods=['POST'])
def validate_otp():
    """
    Validate OTP (generic endpoint).
    
    Expected JSON body:
    {
        "otp": "123456",
        "purpose": "login" | "language"
    }
    """
    data = request.get_json()
    
    if not data.get('otp'):
        return jsonify({
            'success': False,
            'message': 'OTP is required.'
        }), 400
    
    if not data.get('purpose') or data['purpose'] not in ['login', 'language']:
        return jsonify({
            'success': False,
            'message': 'Valid purpose (login/language) is required.'
        }), 400
    
    result = OTPService.validate_otp(data['otp'], data['purpose'])
    
    if result['valid']:
        return jsonify({
            'success': True,
            'valid': True,
            'message': result['message'],
            'otp_type': result['type']
        }), 200
    else:
        return jsonify({
            'success': False,
            'valid': False,
            'message': result['message']
        }), 400


@otp_bp.route('/clear/<purpose>', methods=['POST'])
def clear_otp(purpose):
    """
    Clear OTP for a given purpose (cancel pending verification).
    
    Args:
        purpose: 'login' or 'language'
    """
    if purpose not in ['login', 'language']:
        return jsonify({
            'success': False,
            'message': 'Invalid OTP purpose.'
        }), 400
    
    OTPService.clear_otp(purpose)
    
    # Also clear pending data if clearing login OTP
    if purpose == 'login':
        session.pop('pending_login', None)
    elif purpose == 'language':
        session.pop('pending_language_change', None)
    
    return jsonify({
        'success': True,
        'message': f'{purpose.capitalize()} OTP cleared.'
    }), 200


def mask_target(target: str, otp_type: str) -> str:
    """
    Mask email or mobile number for display.
    
    Args:
        target: Email or mobile number
        otp_type: 'email' or 'mobile'
        
    Returns:
        Masked string (e.g., "use***@gmail.com" or "******7890")
    """
    if not target or target == 'Unknown':
        return 'Unknown'
    
    if otp_type == 'email':
        try:
            local, domain = target.split('@')
            if len(local) > 3:
                masked_local = local[:3] + '***'
            else:
                masked_local = local[0] + '***'
            return f"{masked_local}@{domain}"
        except:
            return target[:3] + '***'
    else:  # mobile
        if len(target) > 4:
            return '******' + target[-4:]
        return '***' + target[-2:]

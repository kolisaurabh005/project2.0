"""
Dashboard Routes Blueprint.
Provides endpoints for user dashboard data including login history
and language change logs.
"""

from flask import Blueprint, jsonify, session
from models import User, LoginHistory, LanguageLog
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


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


@dashboard_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    Get user profile information.
    """
    user = User.get_by_id(session['user_id'])
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found.'
        }), 404
    
    # Get statistics
    login_count = LoginHistory.get_login_count(user['id'])
    unique_devices = LoginHistory.get_unique_devices(user['id'])
    language_stats = LanguageLog.get_language_stats(user['id'])
    current_language = LanguageLog.get_current_language(user['id'])
    
    # Return profile data (excluding password)
    profile_data = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'mobile': user['mobile'],
        'created_at': user['created_at'],
        'stats': {
            'total_logins': login_count,
            'unique_devices': len(unique_devices),
            'languages_used': language_stats,
            'current_language': current_language
        }
    }
    
    return jsonify({
        'success': True,
        'profile': profile_data
    }), 200


@dashboard_bp.route('/login-history', methods=['GET'])
@login_required
def get_login_history():
    """
    Get user's login history.
    Returns the last 50 login records by default.
    """
    user_id = session['user_id']
    
    # Get login history
    history = LoginHistory.get_by_user_id(user_id, limit=50)
    
    # Get unique devices for statistics
    unique_devices = LoginHistory.get_unique_devices(user_id)
    
    return jsonify({
        'success': True,
        'login_history': history,
        'total_count': len(history),
        'unique_devices': unique_devices
    }), 200


@dashboard_bp.route('/recent-logins', methods=['GET'])
@login_required
def get_recent_logins():
    """
    Get login history from the last 24 hours.
    """
    user_id = session['user_id']
    recent_logins = LoginHistory.get_recent_logins(user_id, hours=24)
    
    return jsonify({
        'success': True,
        'recent_logins': recent_logins,
        'count': len(recent_logins),
        'period': '24 hours'
    }), 200


@dashboard_bp.route('/language-history', methods=['GET'])
@login_required
def get_language_history():
    """
    Get user's language change history.
    """
    user_id = session['user_id']
    
    # Get language logs
    history = LanguageLog.get_by_user_id(user_id, limit=50)
    
    # Get language statistics
    language_stats = LanguageLog.get_language_stats(user_id)
    verification_stats = LanguageLog.get_verification_stats(user_id)
    current_language = LanguageLog.get_current_language(user_id)
    
    return jsonify({
        'success': True,
        'language_history': history,
        'total_count': len(history),
        'current_language': current_language,
        'statistics': {
            'by_language': language_stats,
            'by_verification': verification_stats
        }
    }), 200


@dashboard_bp.route('/summary', methods=['GET'])
@login_required
def get_dashboard_summary():
    """
    Get complete dashboard summary with all data.
    """
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found.'
        }), 404
    
    # Get all dashboard data
    login_history = LoginHistory.get_by_user_id(user_id, limit=10)
    recent_logins = LoginHistory.get_recent_logins(user_id, hours=24)
    language_history = LanguageLog.get_by_user_id(user_id, limit=10)
    unique_devices = LoginHistory.get_unique_devices(user_id)
    total_logins = LoginHistory.get_login_count(user_id)
    current_language = LanguageLog.get_current_language(user_id)
    
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'mobile': user['mobile'],
            'created_at': user['created_at']
        },
        'statistics': {
            'total_logins': total_logins,
            'recent_logins_24h': len(recent_logins),
            'unique_devices': len(unique_devices),
            'current_language': current_language
        },
        'recent_login_history': login_history,
        'recent_language_changes': language_history,
        'devices': unique_devices
    }), 200

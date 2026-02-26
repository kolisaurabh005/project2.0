"""
Secure Multi-Language Flask Application
======================================

A production-ready web application featuring:
- User authentication with password hashing
- Browser/device-based access rules
- Multilingual support with OTP verification
- Comprehensive login history tracking

Author: AI Assistant
License: MIT
"""

import os
from flask import Flask, render_template, jsonify
from flask_mail import Mail
from flask_session import Session
from flask_cors import CORS

from config import config
from models import init_app as init_db_app, init_db, get_db
from services import EmailService
from routes import auth_bp, dashboard_bp, otp_bp, language_bp


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function.
    
    Args:
        config_name: Configuration to use ('development', 'production', or 'default')
        
    Returns:
        Configured Flask application instance
    """
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    # Create Flask app
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure required directories exist
    ensure_directories(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize database
    with app.app_context():
        init_database(app)
    
    return app


def ensure_directories(app: Flask):
    """Ensure required directories exist."""
    # Session directory
    session_dir = app.config.get('SESSION_FILE_DIR')
    if session_dir and not os.path.exists(session_dir):
        os.makedirs(session_dir)
    
    # Translations directory
    translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
    if not os.path.exists(translations_dir):
        os.makedirs(translations_dir)


def init_extensions(app: Flask):
    """Initialize Flask extensions."""
    # Initialize CORS
    CORS(app, supports_credentials=True)
    
    # Initialize Flask-Session
    Session(app)
    
    # Initialize Flask-Mail
    mail = Mail(app)
    EmailService.init_app(mail)
    
    # Initialize database
    init_db_app(app)


def register_blueprints(app: Flask):
    """Register Flask blueprints."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(otp_bp)
    app.register_blueprint(language_bp)
    
    # Main route for SPA
    @app.route('/')
    def index():
        """Serve the main single-page application."""
        return render_template('index.html')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'app': 'Secure Multi-Language App',
            'version': '1.0.0'
        })


def register_error_handlers(app: Flask):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


def init_database(app: Flask):
    """Initialize the database."""
    db_path = app.config.get('DATABASE_PATH', 'app.db')
    
    # Check if database needs initialization
    if not os.path.exists(db_path):
        print(f"[DATABASE] Creating new database at {db_path}")
        init_db()
        print("[DATABASE] Database initialized successfully")
    else:
        # Verify tables exist
        try:
            db = get_db()
            db.execute("SELECT 1 FROM users LIMIT 1")
            print(f"[DATABASE] Using existing database at {db_path}")
        except Exception:
            print(f"[DATABASE] Initializing tables in {db_path}")
            init_db()
            print("[DATABASE] Database initialized successfully")


# Create application instance
app = create_app()


if __name__ == '__main__':
    # Run the development server
    print("""
    ========================================
    Secure Multi-Language Flask Application
    ========================================
    
    Server starting...
    
    Access Rules:
    - Chrome Browser: Email OTP required for login
    - Edge Browser: Direct access allowed
    - Mobile Devices: Access only 10 AM - 1 PM
    
    Language Change Rules:
    - French: Email OTP required
    - Other Languages: Mobile OTP required
    
    ========================================
    """)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', True)
    )

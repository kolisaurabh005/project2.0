"""
User model for handling user-related database operations.
Includes password hashing with bcrypt.
"""

import bcrypt
from . import get_db


class User:
    """User model with CRUD operations and authentication helpers."""
    
    @staticmethod
    def create(name: str, email: str, password: str, mobile: str) -> int:
        """
        Create a new user with hashed password.
        
        Args:
            name: User's full name
            email: User's email address (must be unique)
            password: Plain text password (will be hashed)
            mobile: User's mobile number
            
        Returns:
            The ID of the newly created user
            
        Raises:
            sqlite3.IntegrityError: If email already exists
        """
        db = get_db()
        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cursor = db.execute(
            '''INSERT INTO users (name, email, password, mobile) 
               VALUES (?, ?, ?, ?)''',
            (name, email, hashed_password.decode('utf-8'), mobile)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_id(user_id: int) -> dict:
        """
        Get user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            User data as dictionary or None if not found
        """
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        return dict(user) if user else None
    
    @staticmethod
    def get_by_email(email: str) -> dict:
        """
        Get user by email address.
        
        Args:
            email: The user's email address
            
        Returns:
            User data as dictionary or None if not found
        """
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        return dict(user) if user else None
    
    @staticmethod
    def verify_password(email: str, password: str) -> dict:
        """
        Verify user credentials.
        
        Args:
            email: User's email address
            password: Plain text password to verify
            
        Returns:
            User data if credentials are valid, None otherwise
        """
        user = User.get_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None
    
    @staticmethod
    def email_exists(email: str) -> bool:
        """
        Check if email already exists in database.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email exists, False otherwise
        """
        return User.get_by_email(email) is not None
    
    @staticmethod
    def update(user_id: int, **kwargs) -> bool:
        """
        Update user fields.
        
        Args:
            user_id: The user's ID
            **kwargs: Fields to update (name, email, mobile)
            
        Returns:
            True if update successful, False otherwise
        """
        allowed_fields = ['name', 'email', 'mobile']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        db = get_db()
        set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
        values = list(updates.values()) + [user_id]
        
        db.execute(
            f'UPDATE users SET {set_clause} WHERE id = ?',
            values
        )
        db.commit()
        return True
    
    @staticmethod
    def change_password(user_id: int, new_password: str) -> bool:
        """
        Change user's password.
        
        Args:
            user_id: The user's ID
            new_password: New plain text password (will be hashed)
            
        Returns:
            True if password changed successfully
        """
        db = get_db()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        db.execute(
            'UPDATE users SET password = ? WHERE id = ?',
            (hashed_password.decode('utf-8'), user_id)
        )
        db.commit()
        return True

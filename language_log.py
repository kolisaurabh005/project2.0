"""
Language Log model for tracking language change events.
Records language, verification method (email/mobile), and timestamp.
"""

from . import get_db


class LanguageLog:
    """Language Log model with CRUD operations."""
    
    @staticmethod
    def create(user_id: int, language: str, verified_by: str) -> int:
        """
        Record a new language change entry.
        
        Args:
            user_id: The user's ID
            language: Language code (en, hi, es, pt, zh, fr)
            verified_by: Verification method ('email' or 'mobile')
            
        Returns:
            The ID of the new language log entry
        """
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO language_logs (user_id, language, verified_by) 
               VALUES (?, ?, ?)''',
            (user_id, language, verified_by)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_user_id(user_id: int, limit: int = 50) -> list:
        """
        Get language change history for a user, ordered by most recent first.
        
        Args:
            user_id: The user's ID
            limit: Maximum number of records to return
            
        Returns:
            List of language log records as dictionaries
        """
        db = get_db()
        rows = db.execute(
            '''SELECT * FROM language_logs 
               WHERE user_id = ? 
               ORDER BY change_time DESC 
               LIMIT ?''',
            (user_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_current_language(user_id: int) -> str:
        """
        Get the most recently set language for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Language code or 'en' if no history exists
        """
        db = get_db()
        result = db.execute(
            '''SELECT language FROM language_logs 
               WHERE user_id = ? 
               ORDER BY change_time DESC 
               LIMIT 1''',
            (user_id,)
        ).fetchone()
        return result['language'] if result else 'en'
    
    @staticmethod
    def get_language_stats(user_id: int) -> dict:
        """
        Get statistics about language usage for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dictionary with language usage counts
        """
        db = get_db()
        rows = db.execute(
            '''SELECT language, COUNT(*) as count 
               FROM language_logs 
               WHERE user_id = ? 
               GROUP BY language''',
            (user_id,)
        ).fetchall()
        return {row['language']: row['count'] for row in rows}
    
    @staticmethod
    def get_verification_stats(user_id: int) -> dict:
        """
        Get statistics about verification methods used.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dictionary with verification method counts
        """
        db = get_db()
        rows = db.execute(
            '''SELECT verified_by, COUNT(*) as count 
               FROM language_logs 
               WHERE user_id = ? 
               GROUP BY verified_by''',
            (user_id,)
        ).fetchall()
        return {row['verified_by']: row['count'] for row in rows}

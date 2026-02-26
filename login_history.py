"""
Login History model for tracking user logins.
Records IP, browser, OS, device type, and timestamp.
"""

from . import get_db


class LoginHistory:
    """Login History model with CRUD operations."""
    
    @staticmethod
    def create(user_id: int, ip_address: str, browser: str, os: str, device_type: str) -> int:
        """
        Record a new login entry.
        
        Args:
            user_id: The user's ID
            ip_address: Client's IP address
            browser: Browser name (e.g., 'Chrome', 'Firefox')
            os: Operating system (e.g., 'Windows 10', 'macOS')
            device_type: 'desktop' or 'mobile'
            
        Returns:
            The ID of the new login history entry
        """
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO login_history (user_id, ip_address, browser, os, device_type) 
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, ip_address, browser, os, device_type)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_user_id(user_id: int, limit: int = 50) -> list:
        """
        Get login history for a user, ordered by most recent first.
        
        Args:
            user_id: The user's ID
            limit: Maximum number of records to return
            
        Returns:
            List of login history records as dictionaries
        """
        db = get_db()
        rows = db.execute(
            '''SELECT * FROM login_history 
               WHERE user_id = ? 
               ORDER BY login_time DESC 
               LIMIT ?''',
            (user_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_recent_logins(user_id: int, hours: int = 24) -> list:
        """
        Get login history from the last N hours.
        
        Args:
            user_id: The user's ID
            hours: Number of hours to look back
            
        Returns:
            List of recent login records
        """
        db = get_db()
        rows = db.execute(
            '''SELECT * FROM login_history 
               WHERE user_id = ? 
               AND login_time >= datetime('now', '-' || ? || ' hours')
               ORDER BY login_time DESC''',
            (user_id, hours)
        ).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_login_count(user_id: int) -> int:
        """
        Get total number of logins for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Total login count
        """
        db = get_db()
        result = db.execute(
            'SELECT COUNT(*) as count FROM login_history WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        return result['count'] if result else 0
    
    @staticmethod
    def get_unique_devices(user_id: int) -> list:
        """
        Get unique browser/OS combinations used by user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of unique device combinations
        """
        db = get_db()
        rows = db.execute(
            '''SELECT DISTINCT browser, os, device_type 
               FROM login_history 
               WHERE user_id = ?''',
            (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    def delete_old_records(days: int = 90) -> int:
        """
        Delete login history records older than specified days.
        
        Args:
            days: Records older than this will be deleted
            
        Returns:
            Number of records deleted
        """
        db = get_db()
        cursor = db.execute(
            '''DELETE FROM login_history 
               WHERE login_time < datetime('now', '-' || ? || ' days')''',
            (days,)
        )
        db.commit()
        return cursor.rowcount

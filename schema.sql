-- ============================================
-- Database Schema for Secure Multi-Language App
-- ============================================

-- Users table: Stores user credentials and profile information
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- bcrypt hashed password
    mobile VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Login History table: Tracks all login attempts with device information
CREATE TABLE IF NOT EXISTS login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ip_address VARCHAR(45) NOT NULL,  -- Supports IPv6
    browser VARCHAR(100) NOT NULL,
    os VARCHAR(100) NOT NULL,
    device_type VARCHAR(20) NOT NULL,  -- 'desktop' or 'mobile'
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Language Logs table: Records language change events with verification method
CREATE TABLE IF NOT EXISTS language_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    language VARCHAR(10) NOT NULL,  -- en, hi, es, pt, zh, fr
    verified_by VARCHAR(10) NOT NULL,  -- 'email' or 'mobile'
    change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_login_time ON login_history(login_time);
CREATE INDEX IF NOT EXISTS idx_language_logs_user_id ON language_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

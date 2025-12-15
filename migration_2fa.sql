-- Migration to add 2FA support
USE pnpsanjuan_db;

-- Create OTP table for storing verification codes
CREATE TABLE IF NOT EXISTS otp_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    code VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_code (user_id, code),
    INDEX idx_expires (expires_at)
);

-- Add 2FA preference to users table (optional: allow users to enable/disable)
-- Check if column exists before adding
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'pnpsanjuan_db'
    AND TABLE_NAME = 'users'
    AND COLUMN_NAME = 'two_factor_enabled'
);

SET @query = IF(@column_exists = 0,
    'ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT TRUE',
    'SELECT "Column two_factor_enabled already exists" AS message'
);

PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

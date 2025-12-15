-- Migration Script: Add status and updated_at columns to users table
-- Run this if you have an existing database without these columns

USE pnp_san_juan;

-- Add status column with default value 'active'
ALTER TABLE users 
ADD COLUMN status ENUM('active', 'inactive', 'suspended') NOT NULL DEFAULT 'active' AFTER role;

-- Add updated_at timestamp column
ALTER TABLE users 
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

-- Update existing users to active status
UPDATE users SET status = 'active' WHERE status IS NULL;

-- Verify the changes
SELECT id, username, email, role, status, created_at, updated_at FROM users;

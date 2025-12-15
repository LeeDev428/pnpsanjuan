import os
from urllib.parse import urlparse

# Database Configuration - Uses environment variables in production
# Railway provides MYSQLHOST, MYSQLUSER, etc. directly (without ${{...}} syntax)
def get_db_config():
    # Try Railway-style variables first (MYSQLHOST, MYSQLUSER, etc.)
    mysql_host = os.getenv('MYSQLHOST')
    mysql_user = os.getenv('MYSQLUSER')
    mysql_password = os.getenv('MYSQLPASSWORD')
    mysql_database = os.getenv('MYSQLDATABASE')
    mysql_port = os.getenv('MYSQLPORT')
    
    # If Railway variables exist, use them
    if mysql_host:
        return {
            'host': mysql_host,
            'user': mysql_user,
            'password': mysql_password,
            'database': mysql_database,
            'port': int(mysql_port) if mysql_port else 3306
        }
    
    # Otherwise fall back to custom variables or defaults
    return {
        'host': os.getenv('DB_HOST', 'localhost') or 'localhost',
        'user': os.getenv('DB_USER', 'root') or 'root',
        'password': os.getenv('DB_PASSWORD', '') or '',
        'database': os.getenv('DB_NAME', 'pnpsanjuan_db') or 'pnpsanjuan_db',
        'port': int(os.getenv('DB_PORT') or '3306')
    }

DB_CONFIG = get_db_config()

# SMTP Configuration for Gmail 2FA - Uses environment variables in production
SMTP_CONFIG = {
    'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com') or 'smtp.gmail.com',
    'port': int(os.getenv('SMTP_PORT') or '587'),
    'username': os.getenv('SMTP_USERNAME', 'your-email@gmail.com') or 'your-email@gmail.com',
    'password': os.getenv('SMTP_PASSWORD', 'your-app-password') or 'your-app-password',
    'sender_name': os.getenv('SMTP_SENDER_NAME', 'PNP San Juan') or 'PNP San Juan',
    'sender_email': os.getenv('SMTP_SENDER_EMAIL', 'your-email@gmail.com') or 'your-email@gmail.com'
}

# OTP Configuration
OTP_EXPIRY_MINUTES = int(os.getenv('OTP_EXPIRY_MINUTES', '5'))
OTP_LENGTH = int(os.getenv('OTP_LENGTH', '6'))

# Secret Key for Flask sessions
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

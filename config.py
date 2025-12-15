import os

# Database Configuration - Uses environment variables in production
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'pnpsanjuan_db'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

# SMTP Configuration for Gmail 2FA - Uses environment variables in production
SMTP_CONFIG = {
    'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', '587')),
    'username': os.getenv('SMTP_USERNAME', 'your-email@gmail.com'),
    'password': os.getenv('SMTP_PASSWORD', 'your-app-password'),
    'sender_name': os.getenv('SMTP_SENDER_NAME', 'PNP San Juan'),
    'sender_email': os.getenv('SMTP_SENDER_EMAIL', 'your-email@gmail.com')
}

# OTP Configuration
OTP_EXPIRY_MINUTES = int(os.getenv('OTP_EXPIRY_MINUTES', '5'))
OTP_LENGTH = int(os.getenv('OTP_LENGTH', '6'))

# Secret Key for Flask sessions
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

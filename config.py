DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Change this to your MySQL password
    'database': 'pnpsanjuan_db'
}

# SMTP Configuration for Gmail 2FA
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'username': 'your-email@gmail.com',  # Replace with your Gmail address
    'password': 'your-app-password',     # Replace with your Gmail App Password (not regular password)
    'sender_name': 'PNP San Juan',
    'sender_email': 'your-email@gmail.com'
}

# OTP Configuration
OTP_EXPIRY_MINUTES = 5  # OTP valid for 5 minutes
OTP_LENGTH = 6  # 6-digit OTP code

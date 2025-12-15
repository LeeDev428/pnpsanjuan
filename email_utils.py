"""
Email utility module for sending OTP codes via Gmail SMTP
"""
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from config import SMTP_CONFIG, OTP_EXPIRY_MINUTES, OTP_LENGTH
import mysql.connector
from config import DB_CONFIG


def generate_otp(length=OTP_LENGTH):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(recipient_email, otp_code, username):
    """
    Send OTP code via Gmail SMTP
    
    Args:
        recipient_email: User's email address
        otp_code: The OTP code to send
        username: User's username
    
    Returns:
        Boolean indicating success
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your PNP San Juan Login Verification Code'
        msg['From'] = f"{SMTP_CONFIG['sender_name']} <{SMTP_CONFIG['sender_email']}>"
        msg['To'] = recipient_email
        
        # Create HTML and plain text versions
        text_content = f"""
Hello {username},

Your verification code for PNP San Juan is: {otp_code}

This code will expire in {OTP_EXPIRY_MINUTES} minutes.

If you did not attempt to log in, please ignore this email or contact support.

Best regards,
PNP San Juan Team
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .otp-code {{
            font-size: 32px;
            font-weight: bold;
            color: #007bff;
            text-align: center;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            letter-spacing: 5px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        .warning {{
            color: #dc3545;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <h2>PNP San Juan - Login Verification</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>Your verification code for PNP San Juan is:</p>
            <div class="otp-code">{otp_code}</div>
            <p>This code will expire in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
            <p class="warning">⚠️ If you did not attempt to log in, please ignore this email or contact support immediately.</p>
            <div class="footer">
                <p>Best regards,<br>PNP San Juan Team</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        server.starttls()  # Enable TLS encryption
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def store_otp(user_id, otp_code):
    """
    Store OTP code in database
    
    Args:
        user_id: User's ID
        otp_code: The OTP code to store
    
    Returns:
        Boolean indicating success
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Delete any existing unused OTPs for this user
        cursor.execute('DELETE FROM otp_codes WHERE user_id = %s AND is_used = FALSE', (user_id,))
        
        # Calculate expiry time
        expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        # Insert new OTP
        cursor.execute(
            'INSERT INTO otp_codes (user_id, code, expires_at) VALUES (%s, %s, %s)',
            (user_id, otp_code, expires_at)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error storing OTP: {str(e)}")
        return False


def verify_otp(user_id, otp_code):
    """
    Verify OTP code
    
    Args:
        user_id: User's ID
        otp_code: The OTP code to verify
    
    Returns:
        Boolean indicating if OTP is valid
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Find valid OTP
        cursor.execute('''
            SELECT * FROM otp_codes 
            WHERE user_id = %s 
            AND code = %s 
            AND is_used = FALSE 
            AND expires_at > NOW()
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id, otp_code))
        
        otp_record = cursor.fetchone()
        
        if otp_record:
            # Mark OTP as used
            cursor.execute(
                'UPDATE otp_codes SET is_used = TRUE WHERE id = %s',
                (otp_record['id'],)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        
        cursor.close()
        conn.close()
        return False
        
    except Exception as e:
        print(f"Error verifying OTP: {str(e)}")
        return False


def cleanup_expired_otps():
    """Remove expired OTP codes from database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM otp_codes WHERE expires_at < NOW()')
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error cleaning up OTPs: {str(e)}")

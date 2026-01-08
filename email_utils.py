"""
Email utility module for sending OTP codes via SMTP
Supports both Gmail SMTP and SendGrid API
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
import os


def generate_otp(length=OTP_LENGTH):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(recipient_email, otp_code, username):
    """
    Send OTP code via SMTP (Gmail) or SendGrid API
    
    Args:
        recipient_email: User's email address
        otp_code: The OTP code to send
        username: User's username
    
    Returns:
        Boolean indicating success
    """
    print(f"🔧 DEBUG send_otp_email called with:")
    print(f"   Email: {recipient_email}")
    print(f"   OTP: {otp_code}")
    print(f"   Username: {username}")
    print(f"   SMTP Config Username: {SMTP_CONFIG['username']}")
    print(f"   SMTP Config Password: {'*' * len(SMTP_CONFIG['password'])} ({len(SMTP_CONFIG['password'])} chars)")
    
    # Check environment
    is_production = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('MYSQLHOST')
    
    # Try SendGrid first if API key is available
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    if sendgrid_api_key:
        success = send_via_sendgrid(recipient_email, otp_code, username, sendgrid_api_key)
        if success:
            return True
        print("⚠️ SendGrid failed, trying SMTP...")
    
    # Try SMTP as fallback
    print("🔧 DEBUG: Calling send_via_smtp...")
    success = send_via_smtp(recipient_email, otp_code, username)
    print(f"🔧 DEBUG: send_via_smtp returned: {success}")
    
    # In production, if both fail, log OTP for manual verification
    if not success and is_production:
        print(f"⚠️ ALL EMAIL METHODS FAILED IN PRODUCTION")
        print(f"📧 User: {username} ({recipient_email})")
        print(f"🔐 OTP Code: {otp_code}")
        print(f"⏰ Valid for {OTP_EXPIRY_MINUTES} minutes")
        print("💡 Account will be auto-activated as fallback")
    
    return success


def send_via_smtp(recipient_email, otp_code, username):
    """
    Send OTP via traditional SMTP (Gmail)
    Note: May not work on Railway due to port blocking
    """
    print(f"🔧 DEBUG send_via_smtp: Starting SMTP connection...")
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your PNP San Juan Login Verification Code'
        msg['From'] = f"{SMTP_CONFIG['sender_name']} <{SMTP_CONFIG['sender_email']}>"
        msg['To'] = recipient_email
        
        print(f"🔧 DEBUG: Email message created")
        
        # Create HTML and plain text versions
        text_content = f"""
Hello {username},

Your verification code for PNP San Juan is: {otp_code}

This code will expire in {OTP_EXPIRY_MINUTES} minutes.

If you did not attempt to log in, please ignore this email or contact support.

Best regards,
PNP San Juan Team
        """
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }
        .content { background-color: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .otp-code { font-size: 32px; font-weight: bold; color: #007bff; text-align: center; 
                   padding: 20px; background-color: #f8f9fa; border-radius: 5px; letter-spacing: 5px; margin: 20px 0; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; text-align: center; }
        .warning { color: #dc3545; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <h2>PNP San Juan - Login Verification</h2>
            <p>Hello <strong>""" + username + """</strong>,</p>
            <p>Your verification code for PNP San Juan is:</p>
            <div class="otp-code">""" + otp_code + """</div>
            <p>This code will expire in <strong>""" + str(OTP_EXPIRY_MINUTES) + """ minutes</strong>.</p>
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
        
        print(f"🔧 DEBUG: Connecting to SMTP {SMTP_CONFIG['server']}:{SMTP_CONFIG['port']}")
        
        # Connect to SMTP server with timeout
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'], timeout=10)
        print(f"🔧 DEBUG: SMTP connection established, starting TLS...")
        
        server.starttls()  # Enable TLS encryption
        print(f"🔧 DEBUG: TLS enabled, logging in...")
        
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        print(f"🔧 DEBUG: Login successful, sending message...")
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        print(f"✓ Email sent successfully via SMTP to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"✗ Error sending email via SMTP: {str(e)}")
        print(f"✗ Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def send_via_sendgrid(recipient_email, otp_code, username, api_key):
    """
    Send OTP via SendGrid API (works on Railway)
    """
    try:
        import requests
        
        # Generate HTML content (using + for concatenation to avoid f-string escaping issues)
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }
        .content { background-color: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .otp-code { font-size: 32px; font-weight: bold; color: #007bff; text-align: center; 
                     padding: 20px; background-color: #f8f9fa; border-radius: 5px; letter-spacing: 5px; margin: 20px 0; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; text-align: center; }
        .warning { color: #dc3545; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <h2>PNP San Juan - Login Verification</h2>
            <p>Hello <strong>""" + username + """</strong>,</p>
            <p>Your verification code for PNP San Juan is:</p>
            <div class="otp-code">""" + otp_code + """</div>
            <p>This code will expire in <strong>""" + str(OTP_EXPIRY_MINUTES) + """ minutes</strong>.</p>
            <p class="warning">⚠️ If you did not attempt to log in, please ignore this email or contact support immediately.</p>
            <div class="footer">
                <p>Best regards,<br>PNP San Juan Team</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # Plain text version
        text_content = f"""
Hello {username},

Your verification code for PNP San Juan is: {otp_code}

This code will expire in {OTP_EXPIRY_MINUTES} minutes.

If you did not attempt to log in, please ignore this email or contact support.

Best regards,
PNP San Juan Team
        """
        
        # SendGrid API request
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [
                {
                    "to": [{"email": recipient_email}],
                    "subject": "Your PNP San Juan Login Verification Code"
                }
            ],
            "from": {
                "email": SMTP_CONFIG['sender_email'],
                "name": SMTP_CONFIG['sender_name']
            },
            "content": [
                {
                    "type": "text/plain",
                    "value": text_content
                },
                {
                    "type": "text/html",
                    "value": html_content
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 202:
            print(f"✓ Email sent successfully via SendGrid to {recipient_email}")
            return True
        else:
            print(f"✗ SendGrid error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error sending email via SendGrid: {str(e)}")
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

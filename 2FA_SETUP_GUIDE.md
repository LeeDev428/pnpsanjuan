# 2FA Setup Guide - Gmail SMTP

## Overview
This guide will help you set up 2-Factor Authentication (2FA) using Gmail's SMTP server for sending OTP codes.

## Prerequisites
- A Gmail account
- MySQL database running

## Step 1: Set Up Gmail App Password

Since Gmail requires App Passwords for SMTP access (regular passwords won't work), follow these steps:

1. **Enable 2-Step Verification on your Gmail account:**
   - Go to https://myaccount.google.com/security
   - Click on "2-Step Verification" and follow the setup process
   - You MUST enable 2-Step Verification before you can create an App Password

2. **Create an App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" for the app and "Other" for the device
   - Name it "PNP San Juan 2FA" or similar
   - Click "Generate"
   - **Copy the 16-character password** (it will look like: `xxxx xxxx xxxx xxxx`)

## Step 2: Update Configuration

Edit `config.py` and update the SMTP configuration:

```python
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'username': 'your-email@gmail.com',        # Your Gmail address
    'password': 'xxxx xxxx xxxx xxxx',          # The App Password you generated
    'sender_name': 'PNP San Juan',
    'sender_email': 'your-email@gmail.com'     # Your Gmail address
}
```

**Important:** Use the App Password (16 characters), NOT your regular Gmail password!

## Step 3: Run Database Migration

Execute the migration SQL file to add 2FA support to your database:

```powershell
# Using MySQL command line
mysql -u root -p pnpsanjuan_db < migration_2fa.sql

# OR using MySQL Workbench
# Open migration_2fa.sql and execute it
```

This creates:
- `otp_codes` table for storing verification codes
- `two_factor_enabled` column in users table

## Step 4: Test the Setup

1. **Start your Flask application:**
   ```powershell
   python app.py
   ```

2. **Try logging in:**
   - Go to the login page
   - Enter your credentials
   - You should receive an email with a 6-digit OTP code
   - Enter the code on the verification page

## How It Works

### Login Flow:
1. User enters username and password
2. System validates credentials
3. If valid, generates a 6-digit OTP code
4. Sends OTP via Gmail SMTP to user's email
5. Stores OTP in database (expires in 5 minutes)
6. User enters OTP on verification page
7. System validates OTP and completes login

### Security Features:
- ✅ OTP expires after 5 minutes
- ✅ OTP can only be used once
- ✅ Old OTPs are automatically deleted when new one is generated
- ✅ Email sent with both plain text and HTML formatting
- ✅ Secure password hashing with Werkzeug

## Configuration Options

You can customize these settings in `config.py`:

```python
OTP_EXPIRY_MINUTES = 5  # Change OTP expiration time
OTP_LENGTH = 6          # Change OTP code length
```

## Disable 2FA for Specific Users

To disable 2FA for a specific user:

```sql
UPDATE users SET two_factor_enabled = FALSE WHERE username = 'admin';
```

To re-enable:

```sql
UPDATE users SET two_factor_enabled = TRUE WHERE username = 'admin';
```

## Troubleshooting

### "Failed to send verification code"

**Possible causes:**
1. **App Password not set correctly**
   - Make sure you're using the App Password, not your Gmail password
   - Remove any spaces from the App Password

2. **2-Step Verification not enabled**
   - You must enable 2-Step Verification on your Gmail account first

3. **"Less secure app access" blocked**
   - Gmail no longer supports this. You MUST use App Passwords

4. **Firewall blocking SMTP**
   - Ensure port 587 is not blocked by your firewall

### Email not received

1. **Check spam folder**
2. **Verify email address in database:**
   ```sql
   SELECT email FROM users WHERE username = 'your-username';
   ```
3. **Check server logs** for error messages

### OTP Invalid or Expired

1. **Check system time** - Make sure your server time is correct
2. **OTP expires in 5 minutes** - Request a new code if expired
3. **Use "Resend Code"** button on verification page

## Email Template Customization

To customize the OTP email, edit the `send_otp_email()` function in `email_utils.py`:

- Modify `html_content` for visual changes
- Update `text_content` for plain text version
- Change colors, fonts, and layout as needed

## Production Recommendations

1. **Use environment variables** for sensitive data:
   ```python
   import os
   SMTP_CONFIG = {
       'username': os.getenv('SMTP_USERNAME'),
       'password': os.getenv('SMTP_PASSWORD'),
       # ...
   }
   ```

2. **Set up OTP cleanup cron job:**
   ```python
   from email_utils import cleanup_expired_otps
   # Call periodically to remove expired OTPs
   ```

3. **Monitor email sending** for failures and implement retry logic

4. **Consider rate limiting** to prevent OTP spam

## Support

If you encounter issues:
1. Check the console/terminal for error messages
2. Verify all configuration settings
3. Test SMTP connection independently
4. Review database migration success

## Files Modified/Created

- ✅ `migration_2fa.sql` - Database migration
- ✅ `email_utils.py` - Email and OTP utilities
- ✅ `config.py` - SMTP configuration
- ✅ `routes/auth.py` - 2FA authentication logic
- ✅ `templates/verify_otp.html` - OTP verification page
- ✅ `2FA_SETUP_GUIDE.md` - This guide

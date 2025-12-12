# PNP San Juan Web Application

A modern, minimalist web application built with Flask and MySQL.

## Features
- 🏠 Landing page
- 🔐 User authentication (Login/Register)
- 🎨 Modern red theme design
- 🗄️ MySQL database integration

## Quick Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server installed and running

### Installation Steps

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure MySQL Database**
   - Open `config.py`
   - Update the MySQL password:
     ```python
     'password': 'your_mysql_password'
     ```

3. **Create the Database**
   - Open MySQL command line or MySQL Workbench
   - Run:
     ```sql
     CREATE DATABASE pnpsanjuan_db;
     ```

4. **Add Your Logo**
   - Place your `pnpsanjuan.png` file in the `static/images/` directory
   - Recommended size: 180x180 pixels

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the Website**
   - Open your browser and go to: `http://localhost:5000`

## Project Structure
```
pnpsanjuan/
├── app.py                 # Main Flask application
├── config.py              # Database configuration
├── requirements.txt       # Python dependencies
├── database.sql          # Database reference
├── static/
│   ├── css/
│   │   └── style.css     # Modern red theme styles
│   └── images/
│       └── pnpsanjuan.png  # Your logo (add this)
└── templates/
    ├── landing.html      # Home page
    ├── login.html        # Login page
    └── register.html     # Registration page
```

## Usage

### Register a New Account
1. Click "Register" button
2. Fill in username, email, and password
3. Submit the form

### Login
1. Click "Login" button
2. Enter your username and password
3. Click "Sign In"

### Logout
- Click "Logout" button when logged in

## Important Notes

⚠️ **Before Production:**
- Change the `secret_key` in `app.py` to a secure random string
- Update MySQL credentials in `config.py`
- Set `debug=False` in `app.py`
- Use environment variables for sensitive data

## Troubleshooting

**Database Connection Error:**
- Verify MySQL is running
- Check credentials in `config.py`
- Ensure `pnpsanjuan_db` database exists

**Module Not Found Error:**
- Run: `pip install -r requirements.txt`

**Port Already in Use:**
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

## Support
For issues or questions, please check the MySQL connection and ensure all dependencies are installed correctly.

---
© 2025 PNP San Juan. All rights reserved.

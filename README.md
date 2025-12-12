# PNP San Juan Web Application

A modern, minimalist web application built with Flask and MySQL featuring role-based dashboards.

## Features
- 🏠 Landing page
- 🔐 User authentication (Login/Register)
- 👥 **3 User Roles:**
  - **Admin** - System management
  - **Employee** - Full profile with educational background
  - **Applicant** - Application tracking
- 🎨 Modern red theme design
- 📱 Responsive layout
- 🗄️ MySQL database integration

## Project Structure
```
pnpsanjuan/
├── app.py                    # Main Flask application
├── config.py                 # Database configuration
├── seed.py                   # Database seeder script
├── requirements.txt          # Python dependencies
├── database.sql             # Database schema
├── routes/                   # Backend route modules
│   ├── auth.py              # Authentication routes
│   ├── admin.py             # Admin routes
│   ├── employee.py          # Employee routes
│   └── applicant.py         # Applicant routes
├── static/
│   ├── css/
│   │   ├── style.css        # Main styles
│   │   ├── dashboard.css    # Dashboard styles
│   │   └── profile.css      # Profile page styles
│   └── images/
│       └── pnpsanjaun.png   # Logo
└── templates/
    ├── landing.html         # Home page
    ├── login.html           # Login page
    ├── register.html        # Registration page
    ├── partials/            # Reusable components
    │   ├── navbar.html
    │   └── footer.html
    ├── admin/               # Admin pages
    │   ├── dashboard.html
    │   └── profile.html
    ├── employee/            # Employee pages
    │   ├── dashboard.html
    │   └── profile.html
    └── applicant/           # Applicant pages
        ├── dashboard.html
        └── profile.html
```

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

4. **Run the Application (First Time)**
   ```bash
   python app.py
   ```
   This will automatically create all necessary tables.

5. **Seed Test Users (Optional)**
   ```bash
   python seed.py
   ```
   This creates 3 test accounts (see below).

6. **Access the Website**
   - Open your browser and go to: `http://localhost:5000`

## Test Accounts

After running `seed.py`, you can login with:

| Role | Username | Password | Email |
|------|----------|----------|-------|
| **Admin** | admin | password123 | admin@pnpsanjuan.com |
| **Employee** | employee1 | password123 | employee@pnpsanjuan.com |
| **Applicant** | applicant1 | password123 | applicant@pnpsanjuan.com |

## User Roles & Features

### 👨‍💼 Admin
- System overview dashboard
- View basic profile information
- Manage users (coming soon)

### 👮 Employee
- Personal dashboard
- **Complete Profile Management:**
  - General Information (name, unit, station, address)
  - Emergency contact details
  - Educational background section
  - Schooling records section
- Profile dropdown navigation

### 📝 Applicant
- Application tracking dashboard
- Basic profile editing
- Application status monitoring
- Document upload (coming soon)

## Usage

### Register a New Account
1. Click "Register" button
2. Fill in username, email, and password
3. Submit (creates applicant account by default)

### Login
1. Use one of the test accounts or your registered account
2. You'll be redirected to your role-specific dashboard

### Edit Profile
1. Click your username in the navbar
2. Select "Profile" from dropdown
3. Update your information
4. Click "Save Changes"

## Important Notes

⚠️ **Before Production:**
- Change the `secret_key` in `app.py` to a secure random string
- Update MySQL credentials in `config.py`
- Set `debug=False` in `app.py`
- Use environment variables for sensitive data
- Add `.env` file for configuration

## Troubleshooting

**Import Error:**
- Make sure you're in the project directory
- Verify virtual environment is activated

**Database Connection Error:**
- Verify MySQL is running
- Check credentials in `config.py`
- Ensure `pnpsanjuan_db` database exists

**Module Not Found Error:**
- Run: `pip install -r requirements.txt`

**Port Already in Use:**
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

---
© 2025 PNP San Juan. All rights reserved.

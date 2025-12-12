# 🚔 PNP San Juan - Personnel Management System

A comprehensive web-based management system for the Philippine National Police (PNP) San Juan, built with Flask and MySQL. This system streamlines personnel management, recruitment, deployment tracking, and leave applications.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [User Roles](#-user-roles)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)

---

## ✨ Features

### 🔐 Authentication & Authorization
- Role-based access control (Admin, Employee, Applicant)
- Secure password hashing using Werkzeug
- Session management with Flask
- Login/Logout functionality
- User registration for applicants

### 👨‍💼 Admin Module
- **Dashboard**: Overview of system statistics and recent activities
- **User Management**: 
  - Create, read, update, delete (CRUD) operations for all users
  - Filter by role (Admin, Employee, Applicant)
  - Enhanced search functionality
  - User status management (Active, Inactive, Suspended)
  - Profile picture viewing with zoom functionality
- **Recruitment Management**:
  - View all applicant applications
  - Filter by application status (Pending, Approved, Rejected)
  - Update application status
  - View detailed applicant profiles
- **Deployment Management**:
  - Track officer deployments and assignments
  - Manage deployment status (Active, Completed, Cancelled)
  - Station and unit assignment
  - Date tracking (Start/End dates)
- **Reports & Analytics**:
  - Export users data to CSV
  - Export deployments data to CSV
  - Export applicants data to CSV
  - Export leave applications to CSV
  - Custom report generation
- **Profile Management**: Update admin profile information and profile picture

### 👮 Employee Module
- **Dashboard**: Personalized employee dashboard with quick stats
- **Profile Management**: 
  - Comprehensive profile editing
  - Personal information (Name, Rank, Unit, Station)
  - Contact details and emergency contacts
  - Educational background
  - Profile picture upload
- **Leave Applications**:
  - Submit leave requests (Sick Leave, Vacation Leave, Emergency Leave, etc.)
  - View application history with enhanced UI
  - Filter by status with styled dropdowns
  - Edit pending applications
  - Cancel pending applications
  - Automated end date calculation
  - Beautiful form design with modern buttons
- **Personal Records**: View comprehensive personal information

### 📝 Applicant Module
- **Dashboard**: Overview of application status
- **Profile Management**: Complete and update application profile
- **Application Status**: 
  - Visual timeline of application progress
  - Real-time status updates
  - Detailed application information

---

## 🏗️ System Architecture

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │ HTTP/HTTPS
         ▼
┌─────────────────┐
│  Flask Server   │
│   (Python 3.8+) │
├─────────────────┤
│  - Routes       │
│  - Templates    │
│  - Static Files │
└────────┬────────┘
         │ MySQL Connector
         ▼
┌─────────────────┐
│  MySQL Database │
│  (pnpsanjuan_db)│
└─────────────────┘
```

### Technology Stack

**Backend:**
- Flask 3.0.0 - Python web framework
- MySQL Connector Python 8.2.0 - Database driver
- Werkzeug 3.0.1 - Security utilities

**Frontend:**
- HTML5 - Markup
- CSS3 - Styling with modern layouts
- JavaScript (ES6+) - Interactive features
- Font Awesome - Icons

**Database:**
- MySQL 8.0+ - Relational database

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)
- Git (optional)

### Step-by-Step Setup

1. **Clone the repository** (or download ZIP)
   ```bash
   git clone https://github.com/LeeDev428/pnpsanjuan.git
   cd pnpsanjuan
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database**
   ```bash
   # Login to MySQL
   mysql -u root -p

   # Create database
   CREATE DATABASE pnpsanjuan_db;
   exit;
   ```

5. **Import database schema**
   ```bash
   mysql -u root -p pnpsanjuan_db < database.sql
   ```

6. **Configure database connection**
   - Open `config.py`
   - Update MySQL credentials:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_mysql_password',  # Change this
       'database': 'pnpsanjuan_db'
   }
   ```

7. **Seed test users** (optional)
   ```bash
   python seed.py
   ```

8. **Run the application**
   ```bash
   python app.py
   ```

9. **Access the system**
   - Open your browser and navigate to: `http://localhost:5000`

---

## ⚙️ Configuration

### Database Configuration (`config.py`)

```python
DB_CONFIG = {
    'host': 'localhost',        # MySQL server host
    'user': 'root',             # MySQL username
    'password': '',             # MySQL password
    'database': 'pnpsanjuan_db' # Database name
}
```

### Application Configuration (`app.py`)

```python
# Secret key for session management (Change in production!)
app.secret_key = 'your-secret-key-change-this-in-production'

# File upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
```

---

## 💡 Usage

### Default Test Accounts

After running `seed.py`, you can login with these accounts:

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| Admin | `admin` | `password123` | Full system access |
| Employee | `employee1` | `password123` | Employee features |
| Applicant | `applicant1` | `password123` | Applicant features |

### Common Tasks

#### For Admins:
- **Add New Employee**: User Management → Add New User → Select "Employee" role
- **Review Applications**: Recruitment → Filter by status → View details → Update status
- **Manage Deployments**: Deployment → New Deployment → Fill details → Submit
- **Generate Reports**: Reports → Select report type → Export to CSV

#### For Employees:
- **Apply for Leave**: Leave Applications → New Leave Application → Fill form → Submit
- **Update Profile**: My Profile → Edit information → Save
- **View Records**: Personal Records → View comprehensive data

#### For Applicants:
- **Check Status**: Application Status → View timeline
- **Update Profile**: My Profile → Complete application details

---

## 👥 User Roles

### 1. Administrator (Admin)
**Full system control and management**

**Access:**
- Dashboard with system analytics
- User management (CRUD operations)
- Recruitment management
- Deployment tracking
- Reports and data exports
- Profile management

### 2. Employee
**Active PNP personnel**

**Access:**
- Personal dashboard
- Profile management with extensive details
- Leave application system
- Personal records viewer

### 3. Applicant
**Recruitment candidates**

**Access:**
- Application dashboard
- Profile completion
- Application status tracking

---

## 📁 Project Structure

```
pnpsanjuan/
│
├── app.py                      # Main application entry point
├── config.py                   # Database configuration
├── seed.py                     # Database seeder script
├── requirements.txt            # Python dependencies
├── database.sql                # Database schema
├── migrate_database.sql        # Database migrations
├── migration_add_status.sql    # Status field migration
│
├── routes/                     # Application routes (Blueprint structure)
│   ├── auth.py                 # Authentication routes
│   ├── admin.py                # Admin module routes
│   ├── employee.py             # Employee module routes
│   └── applicant.py            # Applicant module routes
│
├── templates/                  # HTML templates (Jinja2)
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── admin/                  # Admin templates
│   ├── employee/               # Employee templates
│   ├── applicant/              # Applicant templates
│   └── partials/               # Reusable components
│
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   │   ├── style.css           # Global styles
│   │   ├── dashboard.css
│   │   ├── profile.css
│   │   ├── users.css
│   │   ├── recruitment.css
│   │   └── deployment.css
│   ├── js/                     # JavaScript files
│   └── uploads/                # User uploads
│       ├── admin/
│       ├── employee/
│       └── applicant/
│
└── __pycache__/                # Python cache files
```

---

## 🗄️ Database Schema

### Core Tables

- **users** - Main authentication table
- **employee_profiles** - Extended employee information
- **applicant_profiles** - Applicant application data
- **admin_profiles** - Administrator information
- **education** - Educational background records
- **deployments** - Deployment tracking
- **leave_applications** - Leave request management

---

## 🔌 API Endpoints

### Authentication Routes
- `GET/POST /login` - User login
- `GET/POST /register` - New applicant registration
- `GET /logout` - User logout

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/recruitment` - Recruitment management
- `GET /admin/deployment` - Deployment management
- `GET /admin/reports` - Reports and analytics

### Employee Routes
- `GET /employee/dashboard` - Employee dashboard
- `GET/POST /employee/profile` - Employee profile
- `GET /employee/leave-applications` - Leave applications
- `POST /employee/leave/add` - Submit leave request

### Applicant Routes
- `GET /applicant/dashboard` - Applicant dashboard
- `GET/POST /applicant/profile` - Applicant profile
- `GET /applicant/application-status` - Application status

---

## 🎨 Recent Enhancements

### UI/UX Improvements
- ✅ Enhanced dropdown styling with custom SVG arrows
- ✅ Modern button design with icons and hover effects
- ✅ Profile picture zoom functionality in user details
- ✅ Improved filter and search boxes across all pages
- ✅ Responsive form layouts with better spacing
- ✅ Smooth animations and transitions

### Technical Updates
- ✅ Fixed profile picture display in admin user view
- ✅ Enhanced CSS with consistent design patterns
- ✅ Improved modal styling and functionality
- ✅ Better form validation and user feedback

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 🐛 Troubleshooting

**Database Connection Error**
- Check MySQL credentials in `config.py`

**Module Not Found**
- Install dependencies: `pip install -r requirements.txt`

**Port Already in Use**
- Change port in `app.py` or stop the process using port 5000

**Upload Folder Not Found**
```bash
mkdir -p static/uploads/admin static/uploads/employee static/uploads/applicant
```

---

## 👨‍💻 Developer

**LeeDev428**
- GitHub: [@LeeDev428](https://github.com/LeeDev428)
- Repository: [pnpsanjuan](https://github.com/LeeDev428/pnpsanjuan)

---

**Built with ❤️ using Flask and Python**

*Last Updated: December 2025*

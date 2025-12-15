# Quick Start Guide - PNP San Juan

## Setup in 5 Steps:

### 1. Create Database
```sql
CREATE DATABASE pnpsanjuan_db;
```

### 2. Update config.py
Change your MySQL password in `config.py`

### 3. Run Application
```bash
python app.py
```

### 4. Seed Test Users
```bash
python seed.py
```

### 5. Login
Go to `http://localhost:5000` and login with:
- **Admin:** admin / password123
- **Employee:** employee1 / password123
- **Applicant:** applicant1 / password123

---

## File Structure Summary:

### Backend Routes (Clean & Organized):
- `routes/auth.py` - Login, Register, Logout
- `routes/admin.py` - Admin dashboard & profile
- `routes/employee.py` - Employee dashboard & profile
- `routes/applicant.py` - Applicant dashboard & profile

### Templates (Role-Based):
- `templates/admin/` - Admin pages
- `templates/employee/` - Employee pages
- `templates/applicant/` - Applicant pages
- `templates/partials/` - Navbar & Footer

### Styling:
- `static/css/style.css` - Main styles + navbar dropdown
- `static/css/dashboard.css` - Dashboard layouts
- `static/css/profile.css` - Profile pages (different for each role)

---

**All done! Simple and organized! 🚀**

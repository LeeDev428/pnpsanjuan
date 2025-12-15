"""
One-time database setup - Access this ONCE via Railway URL
"""
from flask import Flask
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)

@app.route('/SECRET_SETUP_DATABASE_NOW')
def setup():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create all tables
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
              id INT AUTO_INCREMENT PRIMARY KEY,
              username VARCHAR(50) UNIQUE NOT NULL,
              email VARCHAR(100) UNIQUE NOT NULL,
              password VARCHAR(255) NOT NULL,
              role ENUM('admin','employee','applicant') DEFAULT 'applicant',
              status ENUM('active','inactive','suspended') DEFAULT 'active',
              two_factor_enabled BOOLEAN DEFAULT TRUE,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS admin_profiles (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT UNIQUE NOT NULL,
              first_name VARCHAR(100), middle_name VARCHAR(100), last_name VARCHAR(100),
              email VARCHAR(100), phone VARCHAR(20), profile_picture VARCHAR(255),
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS employee_profiles (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT UNIQUE NOT NULL,
              first_name VARCHAR(100), middle_name VARCHAR(100), last_name VARCHAR(100),
              suffix VARCHAR(20), unit VARCHAR(100), station VARCHAR(100),
              address VARCHAR(255), home_address VARCHAR(255),
              gender ENUM('Male','Female','Other'), date_of_birth DATE,
              place_of_birth VARCHAR(100), religion VARCHAR(50),
              emergency_contact_name VARCHAR(100), emergency_relationship VARCHAR(50),
              emergency_contact_number VARCHAR(20), `rank` VARCHAR(50),
              profile_picture VARCHAR(255),
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS applicant_profiles (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT UNIQUE NOT NULL,
              first_name VARCHAR(100), middle_name VARCHAR(100), last_name VARCHAR(100),
              email VARCHAR(100), phone VARCHAR(20), address VARCHAR(255),
              date_of_birth DATE, profile_picture VARCHAR(255),
              application_status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
              applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS education (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT NOT NULL,
              level VARCHAR(50), school_name VARCHAR(200), year_graduated INT,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS deployments (
              id INT AUTO_INCREMENT PRIMARY KEY,
              employee_id INT NOT NULL,
              station VARCHAR(100) NOT NULL, unit VARCHAR(100), position VARCHAR(100),
              start_date DATE NOT NULL, end_date DATE,
              status ENUM('Active','Completed','Cancelled') DEFAULT 'Active',
              remarks TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS leave_applications (
              id INT AUTO_INCREMENT PRIMARY KEY,
              employee_id INT NOT NULL,
              leave_type ENUM('Sick Leave','Vacation Leave','Emergency Leave','Maternity Leave','Paternity Leave') NOT NULL,
              start_date DATE NOT NULL, end_date DATE NOT NULL, days_count INT NOT NULL,
              reason TEXT NOT NULL, status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
              remarks TEXT, applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              reviewed_date TIMESTAMP NULL,
              FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS notifications (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT NOT NULL,
              title VARCHAR(255) NOT NULL, message TEXT NOT NULL,
              type ENUM('applicant','leave','general') NOT NULL,
              related_id INT, is_read BOOLEAN DEFAULT FALSE,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS otp_codes (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT NOT NULL,
              code VARCHAR(6) NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              expires_at TIMESTAMP NOT NULL,
              is_used BOOLEAN DEFAULT FALSE,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )"""
        ]
        
        for sql in tables:
            cursor.execute(sql)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return "<h1>✅ DATABASE SETUP COMPLETE!</h1><p>All 9 tables created. You can now use the app.</p><p><strong>DELETE this setup_db.py file now!</strong></p>"
    
    except Exception as e:
        return f"<h1>❌ ERROR</h1><pre>{str(e)}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

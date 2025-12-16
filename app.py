from flask import Flask, render_template
from dotenv import load_dotenv
from config import DB_CONFIG, SECRET_KEY
import mysql.connector
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configure file uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Import blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.employee import employee_bp
from routes.applicant import applicant_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(applicant_bp)

# Database initialization
def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Create users table with role
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('admin', 'employee', 'applicant') NOT NULL DEFAULT 'applicant',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create employee profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE NOT NULL,
            first_name VARCHAR(100),
            middle_name VARCHAR(100),
            last_name VARCHAR(100),
            suffix VARCHAR(20),
            unit VARCHAR(100),
            station VARCHAR(100),
            address VARCHAR(255),
            home_address VARCHAR(255),
            gender ENUM('Male', 'Female', 'Other'),
            date_of_birth DATE,
            place_of_birth VARCHAR(100),
            religion VARCHAR(50),
            emergency_contact_name VARCHAR(100),
            emergency_relationship VARCHAR(50),
            emergency_contact_number VARCHAR(20),
            `rank` VARCHAR(50),
            profile_picture VARCHAR(255),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create applicant profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applicant_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE NOT NULL,
            first_name VARCHAR(100),
            middle_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(20),
            address VARCHAR(255),
            profile_picture VARCHAR(255),
            application_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create admin profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE NOT NULL,
            first_name VARCHAR(100),
            middle_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(20),
            profile_picture VARCHAR(255),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create education table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            level VARCHAR(50),
            school_name VARCHAR(200),
            year_graduated INT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/SECRET_SETUP_DATABASE_NOW')
def setup_database():
    """ONE-TIME database setup - creates all tables"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Drop and recreate all tables
        tables_sql = [
            "DROP TABLE IF EXISTS otp_codes",
            "DROP TABLE IF EXISTS notifications",
            "DROP TABLE IF EXISTS leave_applications",
            "DROP TABLE IF EXISTS deployments",
            "DROP TABLE IF EXISTS education",
            "DROP TABLE IF EXISTS applicant_profiles",
            "DROP TABLE IF EXISTS employee_profiles",
            "DROP TABLE IF EXISTS admin_profiles",
            "DROP TABLE IF EXISTS users",
            """CREATE TABLE users (
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
            """CREATE TABLE admin_profiles (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT UNIQUE NOT NULL,
              first_name VARCHAR(100), middle_name VARCHAR(100), last_name VARCHAR(100),
              email VARCHAR(100), phone VARCHAR(20), profile_picture VARCHAR(255),
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE employee_profiles (
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
            """CREATE TABLE applicant_profiles (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT UNIQUE NOT NULL,
              first_name VARCHAR(100), middle_name VARCHAR(100), last_name VARCHAR(100),
              email VARCHAR(100), phone VARCHAR(20), address VARCHAR(255),
              date_of_birth DATE, profile_picture VARCHAR(255),
              application_status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
              applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE education (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT NOT NULL,
              level VARCHAR(50), school_name VARCHAR(200), year_graduated INT,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE deployments (
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
            """CREATE TABLE leave_applications (
              id INT AUTO_INCREMENT PRIMARY KEY,
              employee_id INT NOT NULL,
              leave_type ENUM('Sick Leave','Vacation Leave','Emergency Leave','Maternity Leave','Paternity Leave') NOT NULL,
              start_date DATE NOT NULL, end_date DATE NOT NULL, days_count INT NOT NULL,
              reason TEXT NOT NULL, status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
              remarks TEXT, applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              reviewed_date TIMESTAMP NULL,
              FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE notifications (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT NOT NULL,
              title VARCHAR(255) NOT NULL, message TEXT NOT NULL,
              type ENUM('applicant','leave','general') NOT NULL,
              related_id INT, is_read BOOLEAN DEFAULT FALSE,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE otp_codes (
              id INT AUTO_INCREMENT PRIMARY KEY,
              user_id INT NOT NULL,
              code VARCHAR(6) NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              expires_at TIMESTAMP NOT NULL,
              is_used BOOLEAN DEFAULT FALSE,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )"""
        ]
        
        for sql in tables_sql:
            cursor.execute(sql)
        
        conn.commit()
        
        # Verify tables
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return f"""
        <h1 style='color: green;'>✅ DATABASE SETUP COMPLETE!</h1>
        <p><strong>Created {len(tables)} tables:</strong></p>
        <ul>{''.join([f'<li>{t}</li>' for t in tables])}</ul>
        <p><strong>Next steps:</strong></p>
        <ol>
            <li>Run seed.py to create test users</li>
            <li>DELETE the /SECRET_SETUP_DATABASE_NOW route from app.py</li>
        </ol>
        <p><a href="/">Go to homepage</a></p>
        """
    
    except Exception as e:
        return f"<h1 style='color: red;'>❌ ERROR</h1><pre>{str(e)}</pre>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

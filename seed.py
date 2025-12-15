"""
Database seeder script for PNP San Juan
Creates test users for Admin, Employee, and Applicant roles
Password for all users: password123
"""

import mysql.connector
from werkzeug.security import generate_password_hash
from config import DB_CONFIG

def seed_database():
    print("Starting database seeding...")
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Generate password hash for 'password123'
    password_hash = generate_password_hash('password123')
    
    try:
        # Insert admin user
        cursor.execute('''
            INSERT INTO users (username, email, password, role) 
            VALUES (%s, %s, %s, %s)
        ''', ('admin', 'admin@pnpsanjuan.com', password_hash, 'admin'))
        print("✓ Admin user created (username: admin)")
        
        # Insert employee user
        cursor.execute('''
            INSERT INTO users (username, email, password, role) 
            VALUES (%s, %s, %s, %s)
        ''', ('employee1', 'employee@pnpsanjuan.com', password_hash, 'employee'))
        employee_id = cursor.lastrowid
        
        # Create employee profile
        cursor.execute('''
            INSERT INTO employee_profiles (user_id, first_name, middle_name, last_name, `rank`) 
            VALUES (%s, %s, %s, %s, %s)
        ''', (employee_id, 'Juan', 'Dela', 'Cruz', 'PAT'))
        print("✓ Employee user created (username: employee1)")
        
        # Insert applicant user
        cursor.execute('''
            INSERT INTO users (username, email, password, role) 
            VALUES (%s, %s, %s, %s)
        ''', ('applicant1', 'applicant@pnpsanjuan.com', password_hash, 'applicant'))
        applicant_id = cursor.lastrowid
        
        # Create applicant profile
        cursor.execute('''
            INSERT INTO applicant_profiles (user_id, email) 
            VALUES (%s, %s)
        ''', (applicant_id, 'applicant@pnpsanjuan.com'))
        print("✓ Applicant user created (username: applicant1)")
        
        conn.commit()
        print("\n✅ Database seeding completed successfully!")
        print("\nTest accounts:")
        print("  Admin     - username: admin      | password: password123")
        print("  Employee  - username: employee1  | password: password123")
        print("  Applicant - username: applicant1 | password: password123")
        
    except mysql.connector.IntegrityError as e:
        print(f"\n⚠️ Users already exist. Skipping seeding.")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    seed_database()

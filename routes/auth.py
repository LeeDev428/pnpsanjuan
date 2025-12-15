from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import mysql.connector
from config import DB_CONFIG

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash('Access denied', 'error')
                return redirect(url_for('landing'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        from werkzeug.security import check_password_hash
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'employee':
                return redirect(url_for('employee.dashboard'))
            else:
                return redirect(url_for('applicant.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)',
                         (username, email, hashed_password, 'applicant'))
            user_id = cursor.lastrowid
            
            # Create applicant profile
            cursor.execute('INSERT INTO applicant_profiles (user_id, email) VALUES (%s, %s)',
                         (user_id, email))
            
            # Create notification for admins
            cursor.execute('SELECT id FROM users WHERE role = "admin"')
            admins = cursor.fetchall()
            
            for admin in admins:
                cursor.execute('''
                    INSERT INTO notifications (user_id, title, message, type, related_id)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (admin[0], 'New Applicant Registration', 
                      f'New applicant "{username}" has registered.', 'applicant', user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except mysql.connector.IntegrityError:
            flash('Username or email already exists', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('landing'))

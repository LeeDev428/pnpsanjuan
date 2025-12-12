from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from routes.auth import login_required, role_required, get_db_connection
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT profile_picture FROM admin_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin/dashboard.html', profile=profile)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Handle profile picture upload
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"admin_{session['user_id']}_{filename}"
                filepath = os.path.join('static', 'uploads', 'admin', filename)
                file.save(filepath)
                profile_picture = f"uploads/admin/{filename}"
        
        # Check if profile exists
        cursor.execute('SELECT id, profile_picture FROM admin_profiles WHERE user_id = %s', (session['user_id'],))
        existing = cursor.fetchone()
        
        if existing:
            # Delete old profile picture if a new one is uploaded
            if profile_picture and existing['profile_picture']:
                old_file = os.path.join('static', existing['profile_picture'])
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            if profile_picture:
                cursor.execute('''UPDATE admin_profiles SET 
                    first_name=%s, middle_name=%s, last_name=%s, email=%s, phone=%s, profile_picture=%s
                    WHERE user_id=%s''',
                    (first_name, middle_name, last_name, email, phone, profile_picture, session['user_id']))
            else:
                cursor.execute('''UPDATE admin_profiles SET 
                    first_name=%s, middle_name=%s, last_name=%s, email=%s, phone=%s
                    WHERE user_id=%s''',
                    (first_name, middle_name, last_name, email, phone, session['user_id']))
        else:
            cursor.execute('''INSERT INTO admin_profiles 
                (user_id, first_name, middle_name, last_name, email, phone, profile_picture)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                (session['user_id'], first_name, middle_name, last_name, email, phone, profile_picture))
        
        conn.commit()
        flash('Profile updated successfully!', 'success')
    
    # Get profile data
    cursor.execute('SELECT * FROM admin_profiles WHERE user_id = %s', (session['user_id'],))
    admin_profile = cursor.fetchone()
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/profile.html', user=user, profile=admin_profile)

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    tab = request.args.get('tab', 'employees')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get admin profile for navbar
    cursor.execute('SELECT profile_picture FROM admin_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    if tab == 'employees':
        # Count total employees
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "employee"')
        total = cursor.fetchone()['count']
        
        # Get paginated employees with profile data
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.created_at,
                   ep.first_name, ep.middle_name, ep.last_name, ep.`rank`, ep.profile_picture
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            WHERE u.role = "employee"
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        ''', (per_page, offset))
        users_list = cursor.fetchall()
        
        # Count total applicants for badge
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "applicant"')
        applicant_count = cursor.fetchone()['count']
        employee_count = total
        
    else:  # applicants
        # Count total applicants
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "applicant"')
        total = cursor.fetchone()['count']
        
        # Get paginated applicants with profile data
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.created_at,
                   ap.first_name, ap.last_name, ap.application_status, ap.profile_picture
            FROM users u
            LEFT JOIN applicant_profiles ap ON u.id = ap.user_id
            WHERE u.role = "applicant"
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        ''', (per_page, offset))
        users_list = cursor.fetchall()
        
        # Count total employees for badge
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "employee"')
        employee_count = cursor.fetchone()['count']
        applicant_count = total
    
    cursor.close()
    conn.close()
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('admin/users.html',
                         users=users_list,
                         tab=tab,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         employee_count=employee_count,
                         applicant_count=applicant_count,
                         profile=profile)

@admin_bp.route('/users/<int:user_id>/get')
@login_required
@role_required('admin')
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user data
    cursor.execute('SELECT id, username, email, role, status, created_at FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        return {'success': False, 'message': 'User not found'}, 404
    
    # Get profile data based on role
    profile = None
    if user['role'] == 'employee':
        cursor.execute('SELECT * FROM employee_profiles WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()
    elif user['role'] == 'applicant':
        cursor.execute('SELECT * FROM applicant_profiles WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()
    elif user['role'] == 'admin':
        cursor.execute('SELECT * FROM admin_profiles WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return {'success': True, 'user': user, 'profile': profile}

@admin_bp.route('/users/add', methods=['POST'])
@login_required
@role_required('admin')
def add_user():
    from werkzeug.security import generate_password_hash
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    status = request.form.get('status', 'active')
    
    if not all([username, email, password, role]):
        return {'success': False, 'message': 'All fields are required'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if username or email already exists
        cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Username or email already exists'}
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert user
        cursor.execute(
            'INSERT INTO users (username, email, password, role, status) VALUES (%s, %s, %s, %s, %s)',
            (username, email, hashed_password, role, status)
        )
        user_id = cursor.lastrowid
        
        # Create empty profile based on role
        if role == 'employee':
            cursor.execute('INSERT INTO employee_profiles (user_id) VALUES (%s)', (user_id,))
        elif role == 'applicant':
            cursor.execute('INSERT INTO applicant_profiles (user_id) VALUES (%s)', (user_id,))
        elif role == 'admin':
            cursor.execute('INSERT INTO admin_profiles (user_id) VALUES (%s)', (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': f'{role.capitalize()} user created successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error creating user: {str(e)}'}

@admin_bp.route('/users/edit', methods=['POST'])
@login_required
@role_required('admin')
def edit_user():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')
    status = request.form.get('status', 'active')
    
    if not all([user_id, username, email, role]):
        return {'success': False, 'message': 'All fields are required'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if username or email already exists for other users
        cursor.execute(
            'SELECT id FROM users WHERE (username = %s OR email = %s) AND id != %s',
            (username, email, user_id)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Username or email already exists'}
        
        # Update user
        cursor.execute(
            'UPDATE users SET username = %s, email = %s, role = %s, status = %s WHERE id = %s',
            (username, email, role, status, user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'User updated successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error updating user: {str(e)}'}

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    # Prevent deleting own account
    if user_id == session['user_id']:
        return {'success': False, 'message': 'You cannot delete your own account'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Delete user (cascade will delete profile)
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'User not found'}
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'User deleted successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error deleting user: {str(e)}'}


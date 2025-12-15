from flask import Blueprint, render_template, request, session, flash, redirect, url_for, Response
from routes.auth import login_required, role_required, get_db_connection
from werkzeug.utils import secure_filename
import os
import csv
from io import StringIO

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def create_notification(title, message, notif_type, related_id=None):
    """Create a notification for all admin users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all admin users
        cursor.execute('SELECT id FROM users WHERE role = "admin"')
        admins = cursor.fetchall()
        
        # Create notification for each admin
        for admin in admins:
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, related_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (admin[0], title, message, notif_type, related_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error creating notification: {e}")
    finally:
        cursor.close()
        conn.close()


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
                    email=%s, phone=%s, profile_picture=%s
                    WHERE user_id=%s''',
                    (email, phone, profile_picture, session['user_id']))
            else:
                cursor.execute('''UPDATE admin_profiles SET 
                    email=%s, phone=%s
                    WHERE user_id=%s''',
                    (email, phone, session['user_id']))
        else:
            cursor.execute('''INSERT INTO admin_profiles 
                (user_id, email, phone, profile_picture)
                VALUES (%s,%s,%s,%s)''',
                (session['user_id'], email, phone, profile_picture))
        
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
            SELECT u.id, u.username, u.email, u.created_at, u.status,
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
        cursor.execute('SELECT *, profile_picture FROM employee_profiles WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()
    elif user['role'] == 'applicant':
        cursor.execute('SELECT *, profile_picture FROM applicant_profiles WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()
    elif user['role'] == 'admin':
        cursor.execute('SELECT *, profile_picture FROM admin_profiles WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()
    
    # Add profile_picture to user object if available
    if profile and profile.get('profile_picture'):
        user['profile_picture'] = profile['profile_picture']
    
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

@admin_bp.route('/recruitment')
@login_required
@role_required('admin')
def recruitment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get admin profile for nav
    cursor.execute('SELECT profile_picture FROM admin_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get all applicants with pagination
    cursor.execute('''
        SELECT u.id as user_id, u.email as user_email, u.status as account_status,
               ap.first_name, ap.middle_name, ap.last_name, ap.email, ap.phone,
               ap.application_status, ap.applied_date
        FROM users u
        LEFT JOIN applicant_profiles ap ON u.id = ap.user_id
        WHERE u.role = 'applicant'
        ORDER BY ap.applied_date DESC
        LIMIT %s OFFSET %s
    ''', (per_page, offset))
    applicants = cursor.fetchall()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) as total FROM users WHERE role = "applicant"')
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page
    
    cursor.close()
    conn.close()
    
    return render_template('admin/recruitment.html',
                         applicants=applicants,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         profile=profile)

@admin_bp.route('/recruitment/<int:user_id>/view')
@login_required
@role_required('admin')
def view_applicant(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT u.id, u.email as user_email, u.status as account_status,
               ap.first_name, ap.middle_name, ap.last_name, ap.email, ap.phone,
               ap.address, ap.date_of_birth, ap.application_status,
               DATE_FORMAT(ap.applied_date, '%%M %%d, %%Y') as applied_date
        FROM users u
        LEFT JOIN applicant_profiles ap ON u.id = ap.user_id
        WHERE u.id = %s AND u.role = 'applicant'
    ''', (user_id,))
    applicant = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not applicant:
        return {'success': False, 'message': 'Applicant not found'}, 404
    
    return {'success': True, 'applicant': applicant}

@admin_bp.route('/recruitment/update-status', methods=['POST'])
@login_required
@role_required('admin')
def update_applicant_status():
    applicant_id = request.form.get('applicant_id')
    status = request.form.get('status')
    
    if not all([applicant_id, status]):
        return {'success': False, 'message': 'Missing required fields'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            'UPDATE applicant_profiles SET application_status = %s WHERE user_id = %s',
            (status, applicant_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': f'Application status updated to {status}'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error updating status: {str(e)}'}

@admin_bp.route('/recruitment/edit', methods=['POST'])
@login_required
@role_required('admin')
def edit_applicant():
    applicant_id = request.form.get('applicant_id')
    first_name = request.form.get('first_name')
    middle_name = request.form.get('middle_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    date_of_birth = request.form.get('date_of_birth')
    
    if not all([applicant_id, first_name, last_name, email]):
        return {'success': False, 'message': 'Required fields missing'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            UPDATE applicant_profiles 
            SET first_name = %s, middle_name = %s, last_name = %s, 
                email = %s, phone = %s, address = %s, date_of_birth = %s
            WHERE user_id = %s
        ''', (first_name, middle_name, last_name, email, phone, address, 
              date_of_birth if date_of_birth else None, applicant_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'Applicant information updated successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error updating applicant: {str(e)}'}

@admin_bp.route('/leave_applications')
@login_required
@role_required('admin')
def leave_applications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get admin profile
    cursor.execute('SELECT profile_picture FROM admin_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get all leave applications with employee details
    cursor.execute('''
        SELECT la.*,
               CONCAT(ep.first_name, ' ', IFNULL(ep.middle_name, ''), ' ', ep.last_name) as employee_name,
               ep.`rank`
        FROM leave_applications la
        JOIN employee_profiles ep ON la.employee_id = ep.user_id
        ORDER BY la.applied_date DESC
        LIMIT %s OFFSET %s
    ''', (per_page, offset))
    leaves = cursor.fetchall()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) as total FROM leave_applications')
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page
    
    cursor.close()
    conn.close()
    
    return render_template('admin/leave_applications.html',
                         leaves=leaves,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         profile=profile)

@admin_bp.route('/leave/<int:leave_id>/get')
@login_required
@role_required('admin')
def get_leave(leave_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT la.*,
               DATE_FORMAT(la.start_date, '%b %d, %Y') as start_date_formatted,
               DATE_FORMAT(la.end_date, '%b %d, %Y') as end_date_formatted,
               DATE_FORMAT(la.applied_date, '%b %d, %Y') as applied_date_formatted,
               CONCAT(ep.first_name, ' ', IFNULL(ep.middle_name, ''), ' ', ep.last_name) as employee_name,
               ep.`rank`
        FROM leave_applications la
        JOIN employee_profiles ep ON la.employee_id = ep.user_id
        WHERE la.id = %s
    ''', (leave_id,))
    leave = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not leave:
        return {'success': False, 'message': 'Leave application not found'}, 404
    
    return {'success': True, 'leave': leave}

@admin_bp.route('/leave/update-status', methods=['POST'])
@login_required
@role_required('admin')
def update_leave_status():
    leave_id = request.form.get('leave_id')
    status = request.form.get('status')
    remarks = request.form.get('remarks')
    
    if not all([leave_id, status]):
        return {'success': False, 'message': 'Missing required fields'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get leave details for notification
        cursor.execute('''
            SELECT la.employee_id, la.leave_type, la.start_date, la.end_date, u.username
            FROM leave_applications la
            JOIN users u ON la.employee_id = u.id
            WHERE la.id = %s
        ''', (leave_id,))
        leave = cursor.fetchone()
        
        # Update leave status
        cursor.execute(
            'UPDATE leave_applications SET status = %s, remarks = %s WHERE id = %s',
            (status, remarks, leave_id)
        )
        
        # Create notification for employee
        if leave:
            notif_title = f'Leave Application {status}'
            notif_message = f'Your {leave["leave_type"]} from {leave["start_date"].strftime("%b %d, %Y")} to {leave["end_date"].strftime("%b %d, %Y")} has been {status.lower()}.'
            if remarks:
                notif_message += f' Remarks: {remarks}'
            
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, related_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (leave['employee_id'], notif_title, notif_message, 'leave', leave_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': f'Leave application {status.lower()} successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error updating leave status: {str(e)}'}

@admin_bp.route('/notifications/get')
@login_required
@role_required('admin')
def get_notifications():
    """Get recent notifications for admin"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT id, title, message, type, related_id, is_read, created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 50
        ''', (session['user_id'],))
        
        notifications = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {'success': True, 'notifications': notifications}
    
    except Exception as e:
        cursor.close()
        conn.close()
        return {'success': False, 'message': str(e), 'notifications': []}

@admin_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
@role_required('admin')
def mark_notification_read(notif_id):
    """Mark a single notification as read"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE notifications SET is_read = TRUE WHERE id = %s AND user_id = %s',
            (notif_id, session['user_id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': str(e)}

@admin_bp.route('/notifications/read-all', methods=['POST'])
@login_required
@role_required('admin')
def mark_all_notifications_read():
    """Mark all notifications as read"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE',
            (session['user_id'],)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': str(e)}

@admin_bp.route('/deployment')
@login_required
@role_required('admin')
def deployment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get admin profile
    cursor.execute('SELECT profile_picture FROM admin_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Get all employees for dropdown
    cursor.execute('''
        SELECT u.id as user_id,
               CONCAT(ep.first_name, ' ', IFNULL(ep.middle_name, ''), ' ', ep.last_name) as full_name,
               ep.`rank`
        FROM users u
        JOIN employee_profiles ep ON u.id = ep.user_id
        WHERE u.role = 'employee' AND u.status = 'active'
        ORDER BY ep.last_name
    ''')
    employees = cursor.fetchall()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get deployments with officer details
    cursor.execute('''
        SELECT d.*,
               CONCAT(ep.first_name, ' ', IFNULL(ep.middle_name, ''), ' ', ep.last_name) as officer_name,
               ep.`rank`
        FROM deployments d
        JOIN employee_profiles ep ON d.employee_id = ep.user_id
        ORDER BY d.start_date DESC
        LIMIT %s OFFSET %s
    ''', (per_page, offset))
    deployments = cursor.fetchall()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) as total FROM deployments')
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page
    
    cursor.close()
    conn.close()
    
    return render_template('admin/deployment.html',
                         deployments=deployments,
                         employees=employees,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         profile=profile)

@admin_bp.route('/deployment/add', methods=['POST'])
@login_required
@role_required('admin')
def add_deployment():
    employee_id = request.form.get('employee_id')
    station = request.form.get('station')
    unit = request.form.get('unit')
    position = request.form.get('position')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    status = request.form.get('status', 'Active')
    remarks = request.form.get('remarks')
    
    if not all([employee_id, station, start_date]):
        return {'success': False, 'message': 'Required fields missing'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            INSERT INTO deployments (employee_id, station, unit, position, start_date, end_date, status, remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (employee_id, station, unit, position, start_date, end_date if end_date else None, status, remarks))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'Deployment added successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error adding deployment: {str(e)}'}

@admin_bp.route('/deployment/edit', methods=['POST'])
@login_required
@role_required('admin')
def edit_deployment():
    deployment_id = request.form.get('deployment_id')
    employee_id = request.form.get('employee_id')
    station = request.form.get('station')
    unit = request.form.get('unit')
    position = request.form.get('position')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    status = request.form.get('status')
    remarks = request.form.get('remarks')
    
    if not all([deployment_id, employee_id, station, start_date]):
        return {'success': False, 'message': 'Required fields missing'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            UPDATE deployments
            SET employee_id = %s, station = %s, unit = %s, position = %s,
                start_date = %s, end_date = %s, status = %s, remarks = %s
            WHERE id = %s
        ''', (employee_id, station, unit, position, start_date, end_date if end_date else None, status, remarks, deployment_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'Deployment updated successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error updating deployment: {str(e)}'}

@admin_bp.route('/deployment/<int:deployment_id>/get')
@login_required
@role_required('admin')
def get_deployment(deployment_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT d.*,
               DATE_FORMAT(d.start_date, '%b %d, %Y') as start_date_formatted,
               DATE_FORMAT(d.end_date, '%b %d, %Y') as end_date_formatted,
               CONCAT(ep.first_name, ' ', IFNULL(ep.middle_name, ''), ' ', ep.last_name) as officer_name,
               ep.`rank`
        FROM deployments d
        JOIN employee_profiles ep ON d.employee_id = ep.user_id
        WHERE d.id = %s
    ''', (deployment_id,))
    deployment = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not deployment:
        return {'success': False, 'message': 'Deployment not found'}, 404
    
    return {'success': True, 'deployment': deployment}

@admin_bp.route('/deployment/<int:deployment_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_deployment(deployment_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('DELETE FROM deployments WHERE id = %s', (deployment_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Deployment not found'}
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'Deployment deleted successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error deleting deployment: {str(e)}'}

@admin_bp.route('/reports')
@login_required
@role_required('admin')
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get admin profile
    cursor.execute('SELECT profile_picture FROM admin_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "admin"')
    admin_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "employee"')
    employee_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "applicant"')
    applicant_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM deployments WHERE status = "Active"')
    active_deployments = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM deployments WHERE status = "Completed"')
    completed_deployments = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM applicant_profiles WHERE application_status = "Pending"')
    pending_applicants = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM applicant_profiles WHERE application_status = "Approved"')
    approved_applicants = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM applicant_profiles WHERE application_status = "Rejected"')
    rejected_applicants = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM leave_applications WHERE status = "Pending"')
    pending_leaves = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM leave_applications WHERE status = "Approved"')
    approved_leaves = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return render_template('admin/reports.html',
                         profile=profile,
                         admin_count=admin_count,
                         employee_count=employee_count,
                         applicant_count=applicant_count,
                         active_deployments=active_deployments,
                         completed_deployments=completed_deployments,
                         pending_applicants=pending_applicants,
                         approved_applicants=approved_applicants,
                         rejected_applicants=rejected_applicants,
                         pending_leaves=pending_leaves,
                         approved_leaves=approved_leaves)

@admin_bp.route('/reports/export-users')
@login_required
@role_required('admin')
def export_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.role, u.status, u.created_at,
               CASE
                   WHEN u.role = 'employee' THEN CONCAT(ep.first_name, ' ', ep.last_name)
                   WHEN u.role = 'applicant' THEN CONCAT(ap.first_name, ' ', ap.last_name)
                   WHEN u.role = 'admin' THEN CONCAT(adp.first_name, ' ', adp.last_name)
               END as full_name
        FROM users u
        LEFT JOIN employee_profiles ep ON u.id = ep.user_id AND u.role = 'employee'
        LEFT JOIN applicant_profiles ap ON u.id = ap.user_id AND u.role = 'applicant'
        LEFT JOIN admin_profiles adp ON u.id = adp.user_id AND u.role = 'admin'
        ORDER BY u.created_at DESC
    ''')
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Username', 'Full Name', 'Email', 'Role', 'Status', 'Created At'])
    
    for user in users:
        writer.writerow([
            user['id'],
            user['username'],
            user['full_name'] or 'N/A',
            user['email'],
            user['role'],
            user['status'],
            user['created_at'].strftime('%Y-%m-%d %H:%M:%S') if user['created_at'] else ''
        ])
    
    output.seek(0)
    return Response(output.getvalue(),
                   mimetype='text/csv',
                   headers={'Content-Disposition': 'attachment; filename=users_report.csv'})

@admin_bp.route('/reports/export-deployments')
@login_required
@role_required('admin')
def export_deployments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT d.*,
               CONCAT(ep.first_name, ' ', ep.last_name) as officer_name,
               ep.`rank`
        FROM deployments d
        JOIN employee_profiles ep ON d.employee_id = ep.user_id
        ORDER BY d.start_date DESC
    ''')
    deployments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Officer Name', 'Rank', 'Station', 'Unit', 'Position', 'Start Date', 'End Date', 'Status', 'Remarks'])
    
    for d in deployments:
        writer.writerow([
            d['id'],
            d['officer_name'],
            d['rank'] or 'N/A',
            d['station'],
            d['unit'] or 'N/A',
            d['position'] or 'N/A',
            d['start_date'].strftime('%Y-%m-%d') if d['start_date'] else '',
            d['end_date'].strftime('%Y-%m-%d') if d['end_date'] else 'Ongoing',
            d['status'],
            d['remarks'] or ''
        ])
    
    output.seek(0)
    return Response(output.getvalue(),
                   mimetype='text/csv',
                   headers={'Content-Disposition': 'attachment; filename=deployments_report.csv'})

@admin_bp.route('/reports/export-applicants')
@login_required
@role_required('admin')
def export_applicants():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT u.id, u.email as user_email, u.status as account_status,
               ap.first_name, ap.middle_name, ap.last_name, ap.email, ap.phone,
               ap.address, ap.date_of_birth, ap.application_status, ap.applied_date
        FROM users u
        LEFT JOIN applicant_profiles ap ON u.id = ap.user_id
        WHERE u.role = 'applicant'
        ORDER BY ap.applied_date DESC
    ''')
    applicants = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Full Name', 'Email', 'Phone', 'Address', 'Date of Birth', 'Application Status', 'Account Status', 'Applied Date'])
    
    for a in applicants:
        full_name = f"{a['first_name'] or ''} {a['middle_name'] or ''} {a['last_name'] or ''}".strip()
        writer.writerow([
            a['id'],
            full_name or 'N/A',
            a['email'] or a['user_email'],
            a['phone'] or 'N/A',
            a['address'] or 'N/A',
            a['date_of_birth'].strftime('%Y-%m-%d') if a['date_of_birth'] else 'N/A',
            a['application_status'] or 'Pending',
            a['account_status'],
            a['applied_date'].strftime('%Y-%m-%d %H:%M:%S') if a['applied_date'] else ''
        ])
    
    output.seek(0)
    return Response(output.getvalue(),
                   mimetype='text/csv',
                   headers={'Content-Disposition': 'attachment; filename=applicants_report.csv'})

@admin_bp.route('/reports/export-leaves')
@login_required
@role_required('admin')
def export_leaves():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT la.*,
               CONCAT(ep.first_name, ' ', ep.last_name) as employee_name,
               ep.`rank`
        FROM leave_applications la
        JOIN employee_profiles ep ON la.employee_id = ep.user_id
        ORDER BY la.applied_date DESC
    ''')
    leaves = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Employee Name', 'Rank', 'Leave Type', 'Start Date', 'End Date', 'Days', 'Reason', 'Status', 'Applied Date'])
    
    for l in leaves:
        writer.writerow([
            l['id'],
            l['employee_name'],
            l['rank'] or 'N/A',
            l['leave_type'],
            l['start_date'].strftime('%Y-%m-%d') if l['start_date'] else '',
            l['end_date'].strftime('%Y-%m-%d') if l['end_date'] else '',
            l['days_count'],
            l['reason'],
            l['status'],
            l['applied_date'].strftime('%Y-%m-%d %H:%M:%S') if l['applied_date'] else ''
        ])
    
    output.seek(0)
    return Response(output.getvalue(),
                   mimetype='text/csv',
                   headers={'Content-Disposition': 'attachment; filename=leave_applications_report.csv'})

@admin_bp.route('/reports/export-custom')
@login_required
@role_required('admin')
def export_custom():
    report_type = request.args.get('report_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if report_type == 'users':
        cursor.execute('''
            SELECT u.*, 
                   CASE
                       WHEN u.role = 'employee' THEN CONCAT(ep.first_name, ' ', ep.last_name)
                       WHEN u.role = 'applicant' THEN CONCAT(ap.first_name, ' ', ap.last_name)
                       WHEN u.role = 'admin' THEN CONCAT(adp.first_name, ' ', adp.last_name)
                   END as full_name
            FROM users u
            LEFT JOIN employee_profiles ep ON u.id = ep.user_id
            LEFT JOIN applicant_profiles ap ON u.id = ap.user_id
            LEFT JOIN admin_profiles adp ON u.id = adp.user_id
            WHERE DATE(u.created_at) BETWEEN %s AND %s
        ''', (start_date, end_date))
        filename = f'users_{start_date}_to_{end_date}.csv'
        
    elif report_type == 'deployments':
        cursor.execute('''
            SELECT d.*, CONCAT(ep.first_name, ' ', ep.last_name) as officer_name, ep.`rank`
            FROM deployments d
            JOIN employee_profiles ep ON d.employee_id = ep.user_id
            WHERE DATE(d.start_date) BETWEEN %s AND %s
        ''', (start_date, end_date))
        filename = f'deployments_{start_date}_to_{end_date}.csv'
        
    elif report_type == 'applicants':
        cursor.execute('''
            SELECT u.*, ap.*
            FROM users u
            JOIN applicant_profiles ap ON u.id = ap.user_id
            WHERE DATE(ap.applied_date) BETWEEN %s AND %s
        ''', (start_date, end_date))
        filename = f'applicants_{start_date}_to_{end_date}.csv'
        
    elif report_type == 'leaves':
        cursor.execute('''
            SELECT la.*, CONCAT(ep.first_name, ' ', ep.last_name) as employee_name, ep.`rank`
            FROM leave_applications la
            JOIN employee_profiles ep ON la.employee_id = ep.user_id
            WHERE DATE(la.applied_date) BETWEEN %s AND %s
        ''', (start_date, end_date))
        filename = f'leaves_{start_date}_to_{end_date}.csv'
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not data:
        flash('No data found for the selected date range', 'warning')
        return redirect(url_for('admin.reports'))
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    return Response(output.getvalue(),
                   mimetype='text/csv',
                   headers={'Content-Disposition': f'attachment; filename={filename}'})


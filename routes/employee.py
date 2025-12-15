from flask import Blueprint, render_template, request, session, flash, redirect, url_for, current_app
from routes.auth import login_required, role_required, get_db_connection
from werkzeug.utils import secure_filename
import os

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@employee_bp.route('/dashboard')
@login_required
@role_required('employee')
def dashboard():
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get profile with full details
    cursor.execute('''
        SELECT ep.*, u.username, u.email
        FROM employee_profiles ep
        JOIN users u ON ep.user_id = u.id
        WHERE ep.user_id = %s
    ''', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Get leave statistics for current year
    current_year = datetime.now().year
    cursor.execute('''
        SELECT COALESCE(SUM(days_count), 0) as used_days
        FROM leave_applications
        WHERE employee_id = %s AND status = "Approved" AND YEAR(start_date) = %s
    ''', (session['user_id'], current_year))
    used_leave = cursor.fetchone()['used_days'] or 0
    remaining_leave = 15 - used_leave
    
    # Get pending leaves count
    cursor.execute('SELECT COUNT(*) as total FROM leave_applications WHERE employee_id = %s AND status = "Pending"', (session['user_id'],))
    pending_leaves = cursor.fetchone()['total']
    
    # Get recent leave applications
    cursor.execute('''
        SELECT *, DATE_FORMAT(start_date, '%b %d, %Y') as start_formatted,
               DATE_FORMAT(end_date, '%b %d, %Y') as end_formatted
        FROM leave_applications
        WHERE employee_id = %s
        ORDER BY applied_date DESC
        LIMIT 3
    ''', (session['user_id'],))
    recent_leaves = cursor.fetchall()
    
    # Get deployment status
    cursor.execute('''
        SELECT d.*, DATE_FORMAT(d.deployment_date, '%b %d, %Y') as deployment_formatted
        FROM deployments d
        WHERE d.employee_id = %s AND d.status = "Active"
        ORDER BY d.deployment_date DESC
        LIMIT 1
    ''', (session['user_id'],))
    current_deployment = cursor.fetchone()
    
    # Get unread notifications
    cursor.execute('SELECT COUNT(*) as total FROM notifications WHERE user_id = %s AND is_read = FALSE', (session['user_id'],))
    unread_notifs = cursor.fetchone()['total']
    
    cursor.close()
    conn.close()
    
    return render_template('employee/dashboard.html',
                         profile=profile,
                         used_leave=used_leave,
                         remaining_leave=remaining_leave,
                         pending_leaves=pending_leaves,
                         recent_leaves=recent_leaves,
                         current_deployment=current_deployment,
                         unread_notifs=unread_notifs,
                         current_year=current_year)

@employee_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('employee')
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Update profile
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        suffix = request.form.get('suffix')
        unit = request.form.get('unit')
        station = request.form.get('station')
        address = request.form.get('address')
        home_address = request.form.get('home_address')
        gender = request.form.get('gender') or None  # Convert empty string to None
        date_of_birth = request.form.get('date_of_birth') or None
        place_of_birth = request.form.get('place_of_birth')
        religion = request.form.get('religion')
        emergency_contact_name = request.form.get('emergency_contact_name')
        emergency_relationship = request.form.get('emergency_relationship')
        emergency_contact_number = request.form.get('emergency_contact_number')
        rank = request.form.get('rank')
        
        # Handle profile picture upload
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add user_id to filename to make it unique
                filename = f"employee_{session['user_id']}_{filename}"
                filepath = os.path.join('static', 'uploads', 'employee', filename)
                file.save(filepath)
                profile_picture = f"uploads/employee/{filename}"
        
        # Check if profile exists
        cursor.execute('SELECT id, profile_picture FROM employee_profiles WHERE user_id = %s', (session['user_id'],))
        existing = cursor.fetchone()
        
        if existing:
            # Delete old profile picture if a new one is uploaded
            if profile_picture and existing['profile_picture']:
                old_file = os.path.join('static', existing['profile_picture'])
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            # Prepare update query
            if profile_picture:
                cursor.execute('''UPDATE employee_profiles SET 
                    first_name=%s, middle_name=%s, last_name=%s, suffix=%s, unit=%s, station=%s,
                    address=%s, home_address=%s, gender=%s, date_of_birth=%s, place_of_birth=%s,
                    religion=%s, emergency_contact_name=%s, emergency_relationship=%s,
                    emergency_contact_number=%s, `rank`=%s, profile_picture=%s WHERE user_id=%s''',
                    (first_name, middle_name, last_name, suffix, unit, station, address,
                     home_address, gender, date_of_birth, place_of_birth, religion,
                     emergency_contact_name, emergency_relationship, emergency_contact_number,
                     rank, profile_picture, session['user_id']))
            else:
                cursor.execute('''UPDATE employee_profiles SET 
                    first_name=%s, middle_name=%s, last_name=%s, suffix=%s, unit=%s, station=%s,
                    address=%s, home_address=%s, gender=%s, date_of_birth=%s, place_of_birth=%s,
                    religion=%s, emergency_contact_name=%s, emergency_relationship=%s,
                    emergency_contact_number=%s, `rank`=%s WHERE user_id=%s''',
                    (first_name, middle_name, last_name, suffix, unit, station, address,
                     home_address, gender, date_of_birth, place_of_birth, religion,
                     emergency_contact_name, emergency_relationship, emergency_contact_number,
                     rank, session['user_id']))
        else:
            cursor.execute('''INSERT INTO employee_profiles 
                (user_id, first_name, middle_name, last_name, suffix, unit, station, address,
                 home_address, gender, date_of_birth, place_of_birth, religion,
                 emergency_contact_name, emergency_relationship, emergency_contact_number, `rank`, profile_picture)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (session['user_id'], first_name, middle_name, last_name, suffix, unit, station,
                 address, home_address, gender, date_of_birth, place_of_birth, religion,
                 emergency_contact_name, emergency_relationship, emergency_contact_number, rank, profile_picture))
        
        conn.commit()
        flash('Profile updated successfully!', 'success')
        
    # Get profile data
    cursor.execute('SELECT * FROM employee_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('employee/profile.html', user=user, profile=profile)

@employee_bp.route('/personal-records')
@login_required
@role_required('employee')
def personal_records():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get profile for nav
    cursor.execute('SELECT profile_picture FROM employee_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Get employee full details
    cursor.execute('''
        SELECT ep.*, u.status as account_status
        FROM employee_profiles ep
        JOIN users u ON ep.user_id = u.id
        WHERE ep.user_id = %s
    ''', (session['user_id'],))
    employee = cursor.fetchone()
    
    # Get education history
    cursor.execute('''
        SELECT * FROM education
        WHERE user_id = %s
        ORDER BY year_graduated DESC
    ''', (session['user_id'],))
    education = cursor.fetchall()
    
    # Get current deployment
    cursor.execute('''
        SELECT * FROM deployments
        WHERE employee_id = %s AND status = 'Active'
        ORDER BY start_date DESC
        LIMIT 1
    ''', (session['user_id'],))
    deployment = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('employee/personal_records.html',
                         profile=profile,
                         employee=employee,
                         education=education,
                         deployment=deployment)

@employee_bp.route('/leave-applications')
@login_required
@role_required('employee')
def leave_applications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get profile for nav
    cursor.execute('SELECT profile_picture FROM employee_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Calculate leave balance (15 days per year)
    from datetime import datetime
    current_year = datetime.now().year
    
    # Get approved leaves for current year
    cursor.execute('''
        SELECT COALESCE(SUM(days_count), 0) as used_days
        FROM leave_applications
        WHERE employee_id = %s 
        AND status = 'Approved'
        AND YEAR(start_date) = %s
    ''', (session['user_id'], current_year))
    
    used_days = cursor.fetchone()['used_days'] or 0
    total_annual_leave = 15
    remaining_leave = total_annual_leave - used_days
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get leave applications with employee details
    cursor.execute('''
        SELECT la.*, ep.rank, u.username as employee_name
        FROM leave_applications la
        LEFT JOIN employee_profiles ep ON la.employee_id = ep.user_id
        LEFT JOIN users u ON la.employee_id = u.id
        WHERE la.employee_id = %s
        ORDER BY la.applied_date DESC
        LIMIT %s OFFSET %s
    ''', (session['user_id'], per_page, offset))
    leaves = cursor.fetchall()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) as total FROM leave_applications WHERE employee_id = %s', (session['user_id'],))
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page
    
    cursor.close()
    conn.close()
    
    return render_template('employee/leave_applications.html',
                         leaves=leaves,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         profile=profile,
                         total_annual_leave=total_annual_leave,
                         used_leave=used_days,
                         remaining_leave=remaining_leave,
                         current_year=current_year)

@employee_bp.route('/leave/add', methods=['POST'])
@login_required
@role_required('employee')
def add_leave():
    leave_type = request.form.get('leave_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    days_count = request.form.get('days_count')
    reason = request.form.get('reason')
    
    if not all([leave_type, start_date, end_date, days_count, reason]):
        return {'success': False, 'message': 'All fields are required'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            INSERT INTO leave_applications (employee_id, leave_type, start_date, end_date, days_count, reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (session['user_id'], leave_type, start_date, end_date, days_count, reason))
        leave_id = cursor.lastrowid
        
        # Get employee name for notification
        cursor.execute('SELECT username FROM users WHERE id = %s', (session['user_id'],))
        employee = cursor.fetchone()
        employee_name = employee['username'] if employee else 'An employee'
        
        # Create notification for all admins
        cursor.execute('SELECT id FROM users WHERE role = "admin"')
        admins = cursor.fetchall()
        
        for admin in admins:
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, related_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (admin['id'], 'New Leave Application', 
                  f'{employee_name} applied for {leave_type} from {start_date} to {end_date}.', 
                  'leave', leave_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'Leave application submitted successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error submitting leave: {str(e)}'}

@employee_bp.route('/leave/edit', methods=['POST'])
@login_required
@role_required('employee')
def edit_leave():
    leave_id = request.form.get('leave_id')
    leave_type = request.form.get('leave_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    days_count = request.form.get('days_count')
    reason = request.form.get('reason')
    
    if not all([leave_id, leave_type, start_date, end_date, days_count, reason]):
        return {'success': False, 'message': 'All fields are required'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Only allow editing if status is Pending
        cursor.execute('SELECT status FROM leave_applications WHERE id = %s AND employee_id = %s', (leave_id, session['user_id']))
        leave = cursor.fetchone()
        
        if not leave:
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Leave application not found'}
        
        if leave['status'] != 'Pending':
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Cannot edit approved or rejected leave'}
        
        cursor.execute('''
            UPDATE leave_applications
            SET leave_type = %s, start_date = %s, end_date = %s, days_count = %s, reason = %s
            WHERE id = %s AND employee_id = %s
        ''', (leave_type, start_date, end_date, days_count, reason, leave_id, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'Leave application updated successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error updating leave: {str(e)}'}

@employee_bp.route('/leave/<int:leave_id>/get')
@login_required
@role_required('employee')
def get_leave(leave_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT *,
               DATE_FORMAT(start_date, '%b %d, %Y') as start_date_formatted,
               DATE_FORMAT(end_date, '%b %d, %Y') as end_date_formatted,
               DATE_FORMAT(applied_date, '%b %d, %Y') as applied_date_formatted
        FROM leave_applications
        WHERE id = %s AND employee_id = %s
    ''', (leave_id, session['user_id']))
    leave = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not leave:
        return {'success': False, 'message': 'Leave application not found'}, 404
    
    return {'success': True, 'leave': leave}

@employee_bp.route('/leave/<int:leave_id>/delete', methods=['POST'])
@login_required
@role_required('employee')
def delete_leave(leave_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Only allow deletion if status is Pending
        cursor.execute('SELECT status FROM leave_applications WHERE id = %s AND employee_id = %s', (leave_id, session['user_id']))
        leave = cursor.fetchone()
        
        if not leave:
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Leave application not found'}
        
        if leave['status'] != 'Pending':
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Cannot cancel approved or rejected leave'}
        
        cursor.execute('DELETE FROM leave_applications WHERE id = %s AND employee_id = %s', (leave_id, session['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'Leave application cancelled successfully'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error cancelling leave: {str(e)}'}

@employee_bp.route('/notifications/get')
@login_required
@role_required('employee')
def get_notifications():
    """Get recent notifications for employee"""
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

@employee_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
@role_required('employee')
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

@employee_bp.route('/notifications/read-all', methods=['POST'])
@login_required
@role_required('employee')
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

from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from routes.auth import login_required, role_required, get_db_connection
from werkzeug.utils import secure_filename
import os

applicant_bp = Blueprint('applicant', __name__, url_prefix='/applicant')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@applicant_bp.route('/dashboard')
@login_required
@role_required('applicant')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get full applicant profile
    cursor.execute('''
        SELECT ap.*, u.username, u.email, u.created_at,
               DATE_FORMAT(u.created_at, '%b %d, %Y') as registered_date
        FROM applicant_profiles ap
        JOIN users u ON ap.user_id = u.id
        WHERE ap.user_id = %s
    ''', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Calculate profile completion percentage
    profile_fields = ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 
                     'address', 'contact_number', 'email', 'civil_status', 'nationality',
                     'height', 'weight', 'blood_type', 'educational_attainment', 'profile_picture']
    completed_fields = sum(1 for field in profile_fields if profile and profile.get(field))
    profile_completion = int((completed_fields / len(profile_fields)) * 100)
    
    # Get application status (in this case, check if they're still applicant or promoted)
    cursor.execute('SELECT role FROM users WHERE id = %s', (session['user_id'],))
    user_role = cursor.fetchone()['role']
    application_status = 'Pending Review' if user_role == 'applicant' else 'Processed'
    
    # Get unread notifications
    cursor.execute('SELECT COUNT(*) as total FROM notifications WHERE user_id = %s AND is_read = FALSE', (session['user_id'],))
    unread_notifs = cursor.fetchone()['total']
    
    cursor.close()
    conn.close()
    
    return render_template('applicant/dashboard.html',
                         profile=profile,
                         profile_completion=profile_completion,
                         application_status=application_status,
                         unread_notifs=unread_notifs)

@applicant_bp.route('/profile')
@login_required
@role_required('applicant')
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get applicant profile data (read-only)
    cursor.execute('SELECT * FROM applicant_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('applicant/profile.html', user=user, profile=profile)

@applicant_bp.route('/contact-support', methods=['POST'])
@login_required
@role_required('applicant')
def contact_support():
    """Send a support request notification to all admins"""
    message = request.form.get('message')
    subject = request.form.get('subject', 'Profile Edit Request')
    
    if not message:
        return {'success': False, 'message': 'Message is required'}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get applicant details
        cursor.execute('SELECT username FROM users WHERE id = %s', (session['user_id'],))
        applicant = cursor.fetchone()
        applicant_name = applicant['username'] if applicant else 'An applicant'
        
        # Create notification for all admins
        cursor.execute('SELECT id FROM users WHERE role = "admin"')
        admins = cursor.fetchall()
        
        notif_title = f'Support Request: {subject}'
        notif_message = f'{applicant_name} needs assistance: {message}'
        
        for admin in admins:
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, related_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (admin['id'], notif_title, notif_message, 'general', session['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'message': 'Support request sent successfully. Admin will contact you soon.'}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {'success': False, 'message': f'Error sending request: {str(e)}'}

@applicant_bp.route('/application-status')
@login_required
@role_required('applicant')
def application_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get profile for nav
    cursor.execute('SELECT profile_picture FROM applicant_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Get application details
    cursor.execute('''
        SELECT u.status as account_status,
               ap.first_name, ap.middle_name, ap.last_name, ap.email, ap.phone,
               ap.address, ap.date_of_birth, ap.application_status, ap.applied_date
        FROM users u
        LEFT JOIN applicant_profiles ap ON u.id = ap.user_id
        WHERE u.id = %s
    ''', (session['user_id'],))
    application = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('applicant/application_status.html', 
                         profile=profile,
                         application=application)

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
    cursor.execute('SELECT profile_picture FROM applicant_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('applicant/dashboard.html', profile=profile)

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

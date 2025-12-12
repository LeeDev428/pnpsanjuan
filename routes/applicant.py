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

@applicant_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('applicant')
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Handle profile picture upload
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"applicant_{session['user_id']}_{filename}"
                filepath = os.path.join('static', 'uploads', 'applicant', filename)
                file.save(filepath)
                profile_picture = f"uploads/applicant/{filename}"
        
        # Check if profile exists
        cursor.execute('SELECT id, profile_picture FROM applicant_profiles WHERE user_id = %s', (session['user_id'],))
        existing = cursor.fetchone()
        
        if existing:
            # Delete old profile picture if a new one is uploaded
            if profile_picture and existing['profile_picture']:
                old_file = os.path.join('static', existing['profile_picture'])
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            if profile_picture:
                cursor.execute('''UPDATE applicant_profiles SET 
                    first_name=%s, middle_name=%s, last_name=%s, phone=%s, address=%s, profile_picture=%s
                    WHERE user_id=%s''',
                    (first_name, middle_name, last_name, phone, address, profile_picture, session['user_id']))
            else:
                cursor.execute('''UPDATE applicant_profiles SET 
                    first_name=%s, middle_name=%s, last_name=%s, phone=%s, address=%s 
                    WHERE user_id=%s''',
                    (first_name, middle_name, last_name, phone, address, session['user_id']))
        else:
            cursor.execute('''INSERT INTO applicant_profiles 
                (user_id, first_name, middle_name, last_name, phone, address, profile_picture)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                (session['user_id'], first_name, middle_name, last_name, phone, address, profile_picture))
        
        conn.commit()
        flash('Profile updated successfully!', 'success')
    
    cursor.execute('SELECT * FROM applicant_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('applicant/profile.html', user=user, profile=profile)

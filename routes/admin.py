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

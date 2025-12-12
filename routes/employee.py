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
    return render_template('employee/dashboard.html')

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

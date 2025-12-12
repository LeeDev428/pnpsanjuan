from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from routes.auth import login_required, role_required, get_db_connection

applicant_bp = Blueprint('applicant', __name__, url_prefix='/applicant')

@applicant_bp.route('/dashboard')
@login_required
@role_required('applicant')
def dashboard():
    return render_template('applicant/dashboard.html')

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
        
        cursor.execute('''UPDATE applicant_profiles SET 
            first_name=%s, middle_name=%s, last_name=%s, phone=%s, address=%s 
            WHERE user_id=%s''',
            (first_name, middle_name, last_name, phone, address, session['user_id']))
        
        conn.commit()
        flash('Profile updated successfully!', 'success')
    
    cursor.execute('SELECT * FROM applicant_profiles WHERE user_id = %s', (session['user_id'],))
    profile = cursor.fetchone()
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('applicant/profile.html', user=user, profile=profile)

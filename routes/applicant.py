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

@applicant_bp.route('/apply', methods=['GET'])
@login_required
@role_required('applicant')
def application_form():
    """Show the 10-step application form"""
    return render_template('applicant/application_form.html')

@applicant_bp.route('/submit-application', methods=['POST'])
@login_required
@role_required('applicant')
def submit_application():
    """Handle the 10-step application submission"""
    from werkzeug.security import generate_password_hash
    import json
    import uuid
    from datetime import datetime
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        user_id = session['user_id']
        
        # Debug: Print form data
        print("=== FORM DATA RECEIVED ===")
        print(f"First Name: {request.form.get('first_name')}")
        print(f"Last Name: {request.form.get('last_name')}")
        print(f"Gender: {request.form.get('gender')}")
        print(f"Files: {list(request.files.keys())}")
        print("=" * 30)
        
        # Ensure applicant_profiles record exists
        cursor.execute('SELECT id FROM applicant_profiles WHERE user_id = %s', (user_id,))
        profile_exists = cursor.fetchone()
        
        if not profile_exists:
            # Create profile if it doesn't exist
            cursor.execute('INSERT INTO applicant_profiles (user_id) VALUES (%s)', (user_id,))
            conn.commit()
        
        # Step 2: Update Personal Information in applicant_profiles
        cursor.execute('''
            UPDATE applicant_profiles SET
                first_name = %s,
                middle_name = %s,
                last_name = %s,
                suffix = %s,
                gender = %s,
                civil_status = %s,
                date_of_birth = %s,
                place_of_birth = %s,
                citizenship = %s,
                weight_kg = %s,
                height_cm = %s
            WHERE user_id = %s
        ''', (
            request.form.get('first_name'),
            request.form.get('middle_name'),
            request.form.get('last_name'),
            request.form.get('suffix'),
            request.form.get('gender'),
            request.form.get('civil_status'),
            request.form.get('date_of_birth'),
            request.form.get('place_of_birth'),
            request.form.get('citizenship'),
            request.form.get('weight_kg'),
            request.form.get('height_cm'),
            user_id
        ))
        conn.commit()
        
        # Step 3: Insert/Update Address
        cursor.execute('SELECT id FROM applicant_address WHERE user_id = %s', (user_id,))
        address_exists = cursor.fetchone()
        
        if address_exists:
            cursor.execute('''
                UPDATE applicant_address SET
                    house_no = %s, street = %s, barangay = %s, city = %s,
                    zip_code = %s, mobile_number = %s, landline_number = %s
                WHERE user_id = %s
            ''', (
                request.form.get('house_no'),
                request.form.get('street'),
                request.form.get('barangay'),
                request.form.get('city'),
                request.form.get('zip_code'),
                request.form.get('mobile_number'),
                request.form.get('landline_number'),
                user_id
            ))
        else:
            cursor.execute('''
                INSERT INTO applicant_address (user_id, house_no, street, barangay, city, zip_code, mobile_number, landline_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                user_id,
                request.form.get('house_no'),
                request.form.get('street'),
                request.form.get('barangay'),
                request.form.get('city'),
                request.form.get('zip_code'),
                request.form.get('mobile_number'),
                request.form.get('landline_number')
            ))
        
        conn.commit()  # Commit address data
        
        # Step 4: Insert/Update Eligibility
        cursor.execute('SELECT id FROM applicant_eligibility WHERE user_id = %s', (user_id,))
        eligibility_exists = cursor.fetchone()
        
        if eligibility_exists:
            cursor.execute('''
                UPDATE applicant_eligibility SET
                    ra_1080 = %s, ra_6506 = %s, pd_907 = %s,
                    cse_professional = %s, csc_po1 = %s, napolcom = %s
                WHERE user_id = %s
            ''', (
                1 if request.form.get('ra_1080') else 0,
                1 if request.form.get('ra_6506') else 0,
                1 if request.form.get('pd_907') else 0,
                1 if request.form.get('cse_professional') else 0,
                1 if request.form.get('csc_po1') else 0,
                1 if request.form.get('napolcom') else 0,
                user_id
            ))
        else:
            cursor.execute('''
                INSERT INTO applicant_eligibility (user_id, ra_1080, ra_6506, pd_907, cse_professional, csc_po1, napolcom)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                user_id,
                1 if request.form.get('ra_1080') else 0,
                1 if request.form.get('ra_6506') else 0,
                1 if request.form.get('pd_907') else 0,
                1 if request.form.get('cse_professional') else 0,
                1 if request.form.get('csc_po1') else 0,
                1 if request.form.get('napolcom') else 0
            ))
        
        conn.commit()  # Commit eligibility data
        
        # Step 5: Insert/Update Background
        cursor.execute('SELECT id FROM applicant_background WHERE user_id = %s', (user_id,))
        background_exists = cursor.fetchone()
        
        if background_exists:
            cursor.execute('''
                UPDATE applicant_background SET
                    has_criminal_case = %s, criminal_case_details = %s,
                    has_admin_case = %s, admin_case_details = %s,
                    has_previous_pnp_application = %s, previous_pnp_details = %s
                WHERE user_id = %s
            ''', (
                1 if request.form.get('has_criminal_case') else 0,
                request.form.get('criminal_case_details'),
                1 if request.form.get('has_admin_case') else 0,
                request.form.get('admin_case_details'),
                1 if request.form.get('has_previous_pnp_application') else 0,
                request.form.get('previous_pnp_details'),
                user_id
            ))
        else:
            cursor.execute('''
                INSERT INTO applicant_background 
                (user_id, has_criminal_case, criminal_case_details, has_admin_case, admin_case_details, 
                 has_previous_pnp_application, previous_pnp_details)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                user_id,
                1 if request.form.get('has_criminal_case') else 0,
                request.form.get('criminal_case_details'),
                1 if request.form.get('has_admin_case') else 0,
                request.form.get('admin_case_details'),
                1 if request.form.get('has_previous_pnp_application') else 0,
                request.form.get('previous_pnp_details')
            ))
        
        conn.commit()  # Commit background data
        
        # Step 6: Insert Education Records
        # Delete existing education records for this user
        cursor.execute('DELETE FROM education WHERE user_id = %s', (user_id,))
        
        education_levels = [
            ('primary', request.form.get('primary_school'), request.form.get('primary_location'), request.form.get('primary_year')),
            ('secondary', request.form.get('secondary_school'), request.form.get('secondary_location'), request.form.get('secondary_year')),
            ('bachelor', request.form.get('bachelor_school'), request.form.get('bachelor_location'), request.form.get('bachelor_year')),
            ('graduate', request.form.get('graduate_school'), request.form.get('graduate_location'), request.form.get('graduate_year'))
        ]
        
        for level, school, location, year in education_levels:
            if school:  # Only insert if school name is provided
                cursor.execute('''
                    INSERT INTO education (user_id, level, school_name, location, year_graduated, course)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    user_id,
                    level,
                    school,
                    location,
                    year if year else None,
                    request.form.get(f'{level}_course') if level in ['bachelor', 'graduate'] else None
                ))
        
        # Step 7: Insert Character References
        # Delete existing references
        cursor.execute('DELETE FROM character_references WHERE user_id = %s', (user_id,))
        
        for i in range(1, 4):  # References 1-3
            ref_name = request.form.get(f'ref{i}_name')
            if ref_name:  # Only insert if name is provided
                cursor.execute('''
                    INSERT INTO character_references (user_id, reference_name, address, contact_number, relationship)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    user_id,
                    ref_name,
                    request.form.get(f'ref{i}_address'),
                    request.form.get(f'ref{i}_contact'),
                    request.form.get(f'ref{i}_relationship')
                ))
        
        conn.commit()  # Commit character references
        
        # Step 8: Handle File Uploads
        upload_folder = os.path.join('static', 'uploads', 'applicant')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_fields = ['photo_2x2', 'government_id', 'transcript_diploma', 'eligibility_cert']
        
        for field in file_fields:
            if field in request.files:
                file = request.files[field]
                if file and file.filename:
                    filename = secure_filename(f"{user_id}_{field}_{file.filename}")
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    # Store path relative to static folder
                    relative_path = f"uploads/applicant/{filename}"
                    # Update database immediately for this field
                    cursor.execute(f'''
                        UPDATE applicant_profiles 
                        SET {field} = %s 
                        WHERE user_id = %s
                    ''', (relative_path, user_id))
                    print(f"Saved {field}: {relative_path}")  # Debug log
        
        # Commit file uploads
        conn.commit()
        
        # Generate Applicant ID (YY-XXX format)
        current_year = datetime.now().strftime('%y')
        cursor.execute('''
            SELECT COUNT(*) as count FROM applicant_applications 
            WHERE applicant_id LIKE %s
        ''', (f'{current_year}-%',))
        count = cursor.fetchone()['count']
        applicant_id = f"{current_year}-{str(count + 1).zfill(3)}"
        
        # Generate Reference Number
        reference_number = f"PNP-{uuid.uuid4().hex[:8].upper()}"
        
        # Step 10: Create Application Record
        cursor.execute('''
            INSERT INTO applicant_applications 
            (user_id, applicant_id, status, reference_number, step_completed, is_complete)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            user_id,
            applicant_id,
            'SUBMITTED',
            reference_number,
            10,
            True
        ))
        
        application_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Return success response
        return json.dumps({
            'success': True,
            'applicant_id': applicant_id,
            'reference_number': reference_number,
            'pdf_url': url_for('applicant.download_application_pdf', app_id=application_id)
        }), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return json.dumps({
            'success': False,
            'message': str(e)
        }), 500, {'Content-Type': 'application/json'}

@applicant_bp.route('/download-pdf/<int:app_id>')
@login_required
@role_required('applicant')
def download_application_pdf(app_id):
    """Generate and download application PDF"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get application data
        cursor.execute('''
            SELECT app.*, 
                   p.first_name, p.middle_name, p.last_name, p.gender, p.civil_status,
                   p.date_of_birth, p.place_of_birth, p.height_cm, p.weight_kg,
                   addr.house_no, addr.street, addr.barangay, addr.city, addr.zip_code,
                   addr.mobile_number, addr.landline_number
            FROM applicant_applications app
            LEFT JOIN applicant_profiles p ON app.user_id = p.user_id
            LEFT JOIN applicant_address addr ON app.user_id = addr.user_id
            WHERE app.id = %s AND app.user_id = %s
        ''', (app_id, session['user_id']))
        
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not data:
            flash('Application not found', 'error')
            return redirect(url_for('applicant.dashboard'))
        
        # Create simple HTML for PDF
        html_content = f'''
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; }}
                h1 {{ color: #DC143C; }}
                .section {{ margin: 20px 0; }}
                .label {{ font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>PNP San Juan Recruitment Application</h1>
            <div class="section">
                <p><span class="label">Applicant ID:</span> {data['applicant_id']}</p>
                <p><span class="label">Reference Number:</span> {data['reference_number']}</p>
                <p><span class="label">Status:</span> {data['status']}</p>
            </div>
            <div class="section">
                <h2>Personal Information</h2>
                <table>
                    <tr><td class="label">Full Name:</td><td>{data['first_name']} {data['middle_name']} {data['last_name']}</td></tr>
                    <tr><td class="label">Gender:</td><td>{data['gender']}</td></tr>
                    <tr><td class="label">Civil Status:</td><td>{data['civil_status']}</td></tr>
                    <tr><td class="label">Date of Birth:</td><td>{data['date_of_birth']}</td></tr>
                    <tr><td class="label">Place of Birth:</td><td>{data['place_of_birth']}</td></tr>
                    <tr><td class="label">Height:</td><td>{data['height_cm']} cm</td></tr>
                    <tr><td class="label">Weight:</td><td>{data['weight_kg']} kg</td></tr>
                </table>
            </div>
            <div class="section">
                <h2>Contact Information</h2>
                <table>
                    <tr><td class="label">Address:</td><td>{data['house_no']} {data['street']}, {data['barangay']}, {data['city']} {data['zip_code']}</td></tr>
                    <tr><td class="label">Mobile:</td><td>{data['mobile_number']}</td></tr>
                    <tr><td class="label">Landline:</td><td>{data['landline_number'] or 'N/A'}</td></tr>
                </table>
            </div>
        </body>
        </html>
        '''
        
        # Convert to PDF using pdfkit (simpler alternative)
        from io import BytesIO
        from flask import make_response
        
        # For now, return HTML as PDF-like format
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'inline; filename=application_{data["applicant_id"]}.html'
        
        return response
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('applicant.dashboard'))

@applicant_bp.route('/documents')
@login_required
@role_required('applicant')
def documents():
    """Display all uploaded documents"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get applicant profile with document paths
    cursor.execute('''
        SELECT photo_2x2, government_id, transcript_diploma, eligibility_cert
        FROM applicant_profiles 
        WHERE user_id = %s
    ''', (session['user_id'],))
    profile = cursor.fetchone()
    
    # Debug logging
    print(f"=== DOCUMENTS PAGE ===")
    print(f"User ID: {session['user_id']}")
    print(f"Profile data: {profile}")
    print("=" * 30)
    
    cursor.close()
    conn.close()
    
    # Default empty profile if none exists
    if not profile:
        profile = {
            'photo_2x2': None,
            'government_id': None,
            'transcript_diploma': None,
            'eligibility_cert': None
        }
    
    # Check if user has any documents uploaded
    has_documents = any([
        profile.get('photo_2x2'),
        profile.get('government_id'),
        profile.get('transcript_diploma'),
        profile.get('eligibility_cert')
    ])
    
    return render_template('applicant/documents.html', 
                         profile=profile,
                         has_documents=has_documents)

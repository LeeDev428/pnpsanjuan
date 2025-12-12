from flask import Blueprint, render_template, session
from routes.auth import login_required, role_required, get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/profile')
@login_required
@role_required('admin')
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin/profile.html', user=user)

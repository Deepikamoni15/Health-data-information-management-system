from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Mock user database
users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'healthworker': {'password': 'worker123', 'role': 'health_worker'},
    'viewer': {'password': 'viewer123', 'role': 'viewer'}
}

# Complete mock patient data
patients_db = [
    {'id': 1, 'name': 'John Doe', 'age': 35, 'gender': 'Male', 
     'scheme': 'Ayushman Bharat', 'last_visit': '2023-05-15', 'status': 'Active'},
    {'id': 2, 'name': 'Jane Smith', 'age': 28, 'gender': 'Female', 
     'scheme': 'PMJAY', 'last_visit': '2023-06-01', 'status': 'Active'},
    {'id': 3, 'name': 'Robert Johnson', 'age': 42, 'gender': 'Male', 
     'scheme': 'State Health', 'last_visit': '2023-04-22', 'status': 'Inactive'},
    {'id': 4, 'name': 'Emily Davis', 'age': 31, 'gender': 'Female', 
     'scheme': 'Ayushman Bharat', 'last_visit': '2023-06-10', 'status': 'Active'},
    {'id': 5, 'name': 'Michael Brown', 'age': 50, 'gender': 'Male', 
     'scheme': 'Employee Health', 'last_visit': '2023-03-15', 'status': 'Inactive'}
]

# Complete mock health schemes data
schemes_db = [
    {'name': 'Ayushman Bharat', 'enrolled': 1250, 'claims': 892, 
     'active': True, 'start_date': '2020-01-01'},
    {'name': 'PMJAY', 'enrolled': 980, 'claims': 654, 
     'active': True, 'start_date': '2019-05-01'},
    {'name': 'State Health', 'enrolled': 750, 'claims': 420, 
     'active': True, 'start_date': '2021-03-15'},
    {'name': 'Employee Health', 'enrolled': 320, 'claims': 210, 
     'active': False, 'start_date': '2022-01-01'}
]

@app.context_processor
def inject_user():
    return dict(current_user=g.get('current_user'))

@app.before_request
def before_request():
    g.current_user = None
    if 'username' in session:
        g.current_user = {
            'username': session['username'],
            'role': session.get('role')
        }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if g.current_user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.current_user:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_patients = len(patients_db)
    active_schemes = len([s for s in schemes_db if s['active']])
    total_claims = sum(s['claims'] for s in schemes_db)
    recent_patients = sorted(patients_db, key=lambda x: x['last_visit'], reverse=True)[:5]
    
    return render_template('dashboard.html',
                         total_patients=total_patients,
                         active_schemes=active_schemes,
                         total_claims=total_claims,
                         recent_patients=recent_patients,
                         schemes=schemes_db)

@app.route('/patients')
@login_required
def patients():
    return render_template('patients.html', patients=patients_db)

@app.route('/reports')
@login_required
def reports():
    report_types = [
        {'id': 1, 'name': 'Patient Enrollment', 'description': 'Report on patient enrollment by scheme'},
        {'id': 2, 'name': 'Claims Summary', 'description': 'Summary of claims processed'},
        {'id': 3, 'name': 'Scheme Performance', 'description': 'Performance metrics by health scheme'},
        {'id': 4, 'name': 'Monthly Activity', 'description': 'Monthly activity report'}
    ]
    return render_template('reports.html', report_types=report_types)

if __name__ == '__main__':
    app.run(debug=True)
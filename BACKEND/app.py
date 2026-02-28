from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Data files
USERS_FILE = 'users.json'
APPOINTMENTS_FILE = 'appointments.json'
PATIENTS_FILE = 'patients.json'
MEDICAL_RECORDS_FILE = 'medical_records.json'

# Initialize data files if they don't exist
for file in [USERS_FILE, APPOINTMENTS_FILE, PATIENTS_FILE, MEDICAL_RECORDS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

def load_data(filename):
    with open(filename) as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def get_user_by_token(token):
    users = load_data(USERS_FILE)
    for username, info in users.items():
        if info.get('token') == token:
            return username, info
    return None, None

# ==================== AUTH ROUTES ====================

@app.route('/api/register/', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    role = data.get('role', 'patient')
    
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    
    users = load_data(USERS_FILE)
    if username in users:
        return jsonify({'error': 'username already exists'}), 400
    
    token = uuid.uuid4().hex
    users[username] = {
        'password': password, 
        'email': email, 
        'role': role, 
        'token': token,
        'name': data.get('name', '')
    }
    save_data(USERS_FILE, users)
    return jsonify({'message': 'registered', 'token': token, 'role': role})

@app.route('/api/login/', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    
    users = load_data(USERS_FILE)
    user = users.get(username)
    
    if not user or user.get('password') != password:
        return jsonify({'error': 'invalid credentials'}), 400
    
    return jsonify({
        'token': user.get('token'),
        'role': user.get('role'),
        'username': username,
        'name': user.get('name', '')
    })

@app.route('/api/dashboard/', methods=['GET'])
def dashboard():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Token '):
        token = auth.split(' ', 1)[1]
    else:
        return jsonify({'error': 'missing token'}), 401
    
    username, user = get_user_by_token(token)
    if not username:
        return jsonify({'error': 'invalid token'}), 401
    
    return jsonify({
        'username': username, 
        'email': user.get('email'), 
        'role': user.get('role'),
        'name': user.get('name', '')
    })

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/doctors/', methods=['GET'])
def get_doctors():
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'admin':
        return jsonify({'error': 'unauthorized'}), 401
    
    users = load_data(USERS_FILE)
    doctors = [{'username': k, 'email': v.get('email'), 'name': v.get('name')} 
               for k, v in users.items() if v.get('role') == 'doctor']
    return jsonify(doctors)

@app.route('/api/admin/doctors/', methods=['POST'])
def add_doctor():
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'admin':
        return jsonify({'error': 'unauthorized'}), 401
    
    data = request.json or {}
    doctor_username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    name = data.get('name', '')
    
    if not doctor_username or not password:
        return jsonify({'error': 'username and password required'}), 400
    
    users = load_data(USERS_FILE)
    if doctor_username in users:
        return jsonify({'error': 'username already exists'}), 400
    
    token = uuid.uuid4().hex
    users[doctor_username] = {
        'password': password,
        'email': email,
        'role': 'doctor',
        'token': token,
        'name': name
    }
    save_data(USERS_FILE, users)
    return jsonify({'message': 'Doctor added successfully'})

@app.route('/api/admin/doctors/<doctor_username>/', methods=['DELETE'])
def delete_doctor(doctor_username):
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'admin':
        return jsonify({'error': 'unauthorized'}), 401
    
    users = load_data(USERS_FILE)
    if doctor_username not in users or users[doctor_username].get('role') != 'doctor':
        return jsonify({'error': 'Doctor not found'}), 404
    
    del users[doctor_username]
    save_data(USERS_FILE, users)
    return jsonify({'message': 'Doctor deleted successfully'})

@app.route('/api/admin/patients/', methods=['GET'])
def get_all_patients():
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'admin':
        return jsonify({'error': 'unauthorized'}), 401
    
    patients = load_data(PATIENTS_FILE)
    return jsonify(patients)

@app.route('/api/admin/patients/', methods=['POST'])
def add_patient_to_doctor():
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    admin_username, admin_user = get_user_by_token(token or '')
    
    if not admin_username or admin_user.get('role') != 'admin':
        return jsonify({'error': 'unauthorized'}), 401
    
    data = request.json or {}
    patient_username = data.get('patient_username')
    doctor_username = data.get('doctor_username')
    disease = data.get('disease', '')
    
    patients = load_data(PATIENTS_FILE)
    if patient_username not in patients:
        return jsonify({'error': 'Patient not found'}), 404
    
    patients[patient_username]['doctor'] = doctor_username
    patients[patient_username]['disease'] = disease
    save_data(PATIENTS_FILE, patients)
    return jsonify({'message': 'Patient assigned to doctor'})

@app.route('/api/admin/patients/<patient_username>/', methods=['DELETE'])
def admin_delete_patient(patient_username):
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    admin_username, admin_user = get_user_by_token(token or '')
    
    if not admin_username or admin_user.get('role') != 'admin':
        return jsonify({'error': 'unauthorized'}), 401
    
    patients = load_data(PATIENTS_FILE)
    if patient_username in patients:
        del patients[patient_username]
        save_data(PATIENTS_FILE, patients)
    return jsonify({'message': 'Patient deleted successfully'})

# ==================== PATIENT ROUTES ====================

@app.route('/api/patient/profile/', methods=['POST'])
def save_patient_profile():
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'patient':
        return jsonify({'error': 'unauthorized'}), 401
    
    data = request.json or {}
    patients = load_data(PATIENTS_FILE)
    
    patients[username] = {
        'full_name': data.get('full_name', ''),
        'age': data.get('age', ''),
        'marital_status': data.get('marital_status', ''),
        'gender': data.get('gender', ''),
        'address': data.get('address', ''),
        'phone': data.get('phone', ''),
        'email': data.get('email', ''),
        'disease': data.get('disease', ''),
        'doctor': '',
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    save_data(PATIENTS_FILE, patients)
    return jsonify({'message': 'Profile saved successfully'})

@app.route('/api/patient/profile/', methods=['GET'])
def get_patient_profile():
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'patient':
        return jsonify({'error': 'unauthorized'}), 401
    
    patients = load_data(PATIENTS_FILE)
    profile = patients.get(username, {})
    return jsonify(profile)

@app.route('/api/patient/appointment/', methods=['POST'])
def make_appointment():
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'patient':
        return jsonify({'error': 'unauthorized'}), 401
    
    data = request.json or {}
    appointments = load_data(APPOINTMENTS_FILE)
    
    appointment_id = uuid.uuid4().hex
    appointments[appointment_id] = {
        'patient_username': username,
        'doctor_username': data.get('doctor_username', ''),
        'disease': data.get('disease', ''),
        'status': 'pending',
        'appointment_date': data.get('appointment_date', ''),
        'created_at': datetime.now().isoformat()
    }
    save_data(APPOINTMENTS_FILE, appointments)
    
    # Update patient status
    patients = load_data(PATIENTS_FILE)
    if username in patients:
        patients[username]['status'] = 'appointment_pending'
        save_data(PATIENTS_FILE, patients)
    
    return jsonify({'message': 'Appointment requested successfully', 'appointment_id': appointment_id})

# ==================== DOCTOR ROUTES ====================

@app.route('/api/doctor/patients/', methods=['GET'])
def get_doctor_patients():
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'doctor':
        return jsonify({'error': 'unauthorized'}), 401
    
    patients = load_data(PATIENTS_FILE)
    doctor_patients = {k: v for k, v in patients.items() if v.get('doctor') == username}
    return jsonify(doctor_patients)

@app.route('/api/doctor/patients/<patient_username>/discharge/', methods=['POST'])
def discharge_patient(patient_username):
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'doctor':
        return jsonify({'error': 'unauthorized'}), 401
    
    patients = load_data(PATIENTS_FILE)
    if patient_username in patients and patients[patient_username].get('doctor') == username:
        patients[patient_username]['status'] = 'discharged'
        patients[patient_username]['discharged_at'] = datetime.now().isoformat()
        save_data(PATIENTS_FILE, patients)
        return jsonify({'message': 'Patient discharged successfully'})
    
    return jsonify({'error': 'Patient not found or unauthorized'}), 404

@app.route('/api/doctor/patients/<patient_username>/sign/', methods=['POST'])
def sign_patient(patient_username):
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'doctor':
        return jsonify({'error': 'unauthorized'}), 401
    
    patients = load_data(PATIENTS_FILE)
    if patient_username in patients and patients[patient_username].get('doctor') == username:
        patients[patient_username]['status'] = 'under_treatment'
        patients[patient_username]['signed_at'] = datetime.now().isoformat()
        save_data(PATIENTS_FILE, patients)
        return jsonify({'message': 'Patient signed successfully'})
    
    return jsonify({'error': 'Patient not found or unauthorized'}), 404

@app.route('/api/doctor/patients/<patient_username>/', methods=['DELETE'])
def delete_patient(patient_username):
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'doctor':
        return jsonify({'error': 'unauthorized'}), 401
    
    patients = load_data(PATIENTS_FILE)
    if patient_username in patients and patients[patient_username].get('doctor') == username:
        del patients[patient_username]
        save_data(PATIENTS_FILE, patients)
        return jsonify({'message': 'Patient deleted successfully'})
    
    return jsonify({'error': 'Patient not found or unauthorized'}), 404

# ==================== MEDICAL RECORDS ROUTES ====================

@app.route('/api/medical-records/', methods=['GET'])
def get_medical_records():
    """Get medical records - patients see their own, doctors see their patients' records"""
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') not in ['patient', 'doctor', 'admin']:
        return jsonify({'error': 'unauthorized'}), 401
    
    records = load_data(MEDICAL_RECORDS_FILE)
    patients = load_data(PATIENTS_FILE)
    
    if user.get('role') == 'patient':
        # Patient sees only their own records
        patient_records = {k: v for k, v in records.items() if v.get('patient_username') == username}
        return jsonify(patient_records)
    elif user.get('role') == 'doctor':
        # Doctor sees records for their assigned patients
        doctor_patients = [k for k, v in patients.items() if v.get('doctor') == username]
        doctor_records = {k: v for k, v in records.items() if v.get('patient_username') in doctor_patients}
        return jsonify(doctor_records)
    else:
        # Admin sees all records
        return jsonify(records)

@app.route('/api/medical-records/', methods=['POST'])
def create_medical_record():
    """Create a medical record (doctor only)"""
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'doctor':
        return jsonify({'error': 'unauthorized'}), 401
    
    data = request.json or {}
    patient_username = data.get('patient_username')
    
    if not patient_username:
        return jsonify({'error': 'patient_username required'}), 400
    
    # Verify patient is assigned to this doctor
    patients = load_data(PATIENTS_FILE)
    if patient_username not in patients or patients[patient_username].get('doctor') != username:
        return jsonify({'error': 'Patient not found or not assigned to you'}), 404
    
    records = load_data(MEDICAL_RECORDS_FILE)
    
    record_id = uuid.uuid4().hex
    records[record_id] = {
        'patient_username': patient_username,
        'doctor_username': username,
        'diagnosis': data.get('diagnosis', ''),
        'treatment': data.get('treatment', ''),
        'medications': data.get('medications', ''),
        'notes': data.get('notes', ''),
        'created_at': datetime.now().isoformat()
    }
    save_data(MEDICAL_RECORDS_FILE, records)
    return jsonify({'message': 'Medical record created successfully', 'record_id': record_id})

@app.route('/api/medical-records/<record_id>/', methods=['PUT'])
def update_medical_record(record_id):
    """Update a medical record (doctor only)"""
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') != 'doctor':
        return jsonify({'error': 'unauthorized'}), 401
    
    data = request.json or {}
    records = load_data(MEDICAL_RECORDS_FILE)
    
    if record_id not in records:
        return jsonify({'error': 'Record not found'}), 404
    
    # Verify doctor owns this record
    if records[record_id].get('doctor_username') != username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Update fields
    if 'diagnosis' in data:
        records[record_id]['diagnosis'] = data['diagnosis']
    if 'treatment' in data:
        records[record_id]['treatment'] = data['treatment']
    if 'medications' in data:
        records[record_id]['medications'] = data['medications']
    if 'notes' in data:
        records[record_id]['notes'] = data['notes']
    
    records[record_id]['updated_at'] = datetime.now().isoformat()
    save_data(MEDICAL_RECORDS_FILE, records)
    return jsonify({'message': 'Medical record updated successfully'})

# ==================== APPOINTMENT CALENDAR ROUTES ====================

@app.route('/api/appointments/', methods=['GET'])
def get_all_appointments():
    """Get all appointments based on user role"""
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') not in ['patient', 'doctor', 'admin']:
        return jsonify({'error': 'unauthorized'}), 401
    
    appointments = load_data(APPOINTMENTS_FILE)
    patients = load_data(PATIENTS_FILE)
    
    if user.get('role') == 'patient':
        # Patient sees their own appointments
        patient_appointments = {k: v for k, v in appointments.items() if v.get('patient_username') == username}
        return jsonify(patient_appointments)
    elif user.get('role') == 'doctor':
        # Doctor sees appointments for their patients
        doctor_patients = [k for k, v in patients.items() if v.get('doctor') == username]
        doctor_appointments = {k: v for k, v in appointments.items() if v.get('patient_username') in doctor_patients}
        return jsonify(doctor_appointments)
    else:
        # Admin sees all appointments
        return jsonify(appointments)

@app.route('/api/appointments/calendar/', methods=['GET'])
def get_calendar_appointments():
    """Get appointments for calendar view by date range"""
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') not in ['patient', 'doctor', 'admin']:
        return jsonify({'error': 'unauthorized'}), 401
    
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    appointments = load_data(APPOINTMENTS_FILE)
    patients = load_data(PATIENTS_FILE)
    
    filtered_appointments = {}
    
    for appointment_id, appointment in appointments.items():
        appointment_date = appointment.get('appointment_date', '')
        
        # Filter by date range if provided
        if start_date and appointment_date < start_date:
            continue
        if end_date and appointment_date > end_date:
            continue
        
        # Filter by role
        if user.get('role') == 'patient':
            if appointment.get('patient_username') == username:
                filtered_appointments[appointment_id] = appointment
        elif user.get('role') == 'doctor':
            doctor_patients = [k for k, v in patients.items() if v.get('doctor') == username]
            if appointment.get('patient_username') in doctor_patients:
                filtered_appointments[appointment_id] = appointment
        else:
            filtered_appointments[appointment_id] = appointment
    
    return jsonify(filtered_appointments)

@app.route('/api/appointments/<appointment_id>/', methods=['PUT'])
def update_appointment(appointment_id):
    """Update appointment status (doctor/admin only)"""
    auth = request.headers.get('Authorization', '')
    token = auth.split(' ', 1)[1] if auth.startswith('Token ') else None
    username, user = get_user_by_token(token or '')
    
    if not username or user.get('role') not in ['doctor', 'admin']:
        return jsonify({'error': 'unauthorized'}), 401
    
    data = request.json or {}
    appointments = load_data(APPOINTMENTS_FILE)
    
    if appointment_id not in appointments:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Update fields
    if 'status' in data:
        appointments[appointment_id]['status'] = data['status']
    if 'appointment_date' in data:
        appointments[appointment_id]['appointment_date'] = data['appointment_date']
    if 'notes' in data:
        appointments[appointment_id]['notes'] = data['notes']
    
    appointments[appointment_id]['updated_at'] = datetime.now().isoformat()
    save_data(APPOINTMENTS_FILE, appointments)
    return jsonify({'message': 'Appointment updated successfully'})

if __name__ == '__main__':
    app.run(port=8000, debug=True)

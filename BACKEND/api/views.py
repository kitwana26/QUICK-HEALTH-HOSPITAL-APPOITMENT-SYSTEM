from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User, Patient, Appointment, MedicalRecord, Bill, Payment, Notification
from .serializers import (
    UserSerializer, PatientSerializer, AppointmentSerializer,
    MedicalRecordSerializer, RegisterSerializer, LoginSerializer,
    BillSerializer, PaymentSerializer, NotificationSerializer
)


# ==================== AUTH VIEWS ====================

class RegisterView(APIView):
    """Handle user registration"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
            role = data.get('role', 'patient')
            name = data.get('name', '')
            
            if not username or not password:
                return Response({'error': 'username and password required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(username=username).exists():
                return Response({'error': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                role=role,
                first_name=name,
            )
            
            # Create patient profile if role is patient
            if role == 'patient':
                Patient.objects.create(user=user)
            
            return Response({
                'message': 'registered',
                'token': user.token,
                'role': role
            })
        except Exception as e:
            import traceback
            return Response({
                'error': f'Registration failed: {str(e)}',
                'details': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    """Handle user login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({'error': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'token': user.token,
            'role': user.role,
            'username': user.username,
            'name': user.first_name
        })


class DashboardView(APIView):
    """Get user dashboard info"""
    
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'name': user.first_name
        })


# ==================== ADMIN VIEWS ====================

class AdminDoctorView(APIView):
    """Admin doctor management"""
    
    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        doctors = User.objects.filter(role='doctor')
        data = [{'username': d.username, 'email': d.email, 'name': d.first_name} for d in doctors]
        return Response(data)
    
    def post(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        doctor_username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        name = data.get('name', '')
        
        if not doctor_username or not password:
            return Response({'error': 'username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=doctor_username).exists():
            return Response({'error': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        doctor = User.objects.create_user(
            username=doctor_username,
            password=password,
            email=email,
            role='doctor',
            first_name=name,
        )
        
        return Response({'message': 'Doctor added successfully'})


class AdminDoctorDetailView(APIView):
    """Admin doctor detail - delete doctor"""
    
    def delete(self, request, doctor_username):
        if request.user.role != 'admin':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            doctor = User.objects.get(username=doctor_username, role='doctor')
            doctor.delete()
            return Response({'message': 'Doctor deleted successfully'})
        except User.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)


class AdminPatientView(APIView):
    """Admin patient management"""
    
    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        patients = Patient.objects.select_related('user').all()
        data = {}
        for p in patients:
            data[p.user.username] = {
                'full_name': p.full_name,
                'age': p.age,
                'marital_status': p.marital_status,
                'gender': p.gender,
                'address': p.address,
                'phone': p.phone,
                'email': p.email,
                'disease': p.disease,
                'doctor': p.doctor.username if p.doctor else '',
                'status': p.status,
                'created_at': p.created_at.isoformat() if p.created_at else ''
            }
        return Response(data)
    
    def post(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        patient_username = data.get('patient_username')
        doctor_username = data.get('doctor_username')
        disease = data.get('disease', '')
        
        try:
            patient = Patient.objects.get(user__username=patient_username)
            if doctor_username:
                doctor = User.objects.get(username=doctor_username, role='doctor')
                patient.doctor = doctor
            patient.disease = disease
            patient.save()
            return Response({'message': 'Patient assigned to doctor'})
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)


class AdminPatientDetailView(APIView):
    """Admin patient detail - delete patient"""
    
    def delete(self, request, patient_username):
        if request.user.role != 'admin':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            patient = Patient.objects.get(user__username=patient_username)
            patient.user.delete()
            return Response({'message': 'Patient deleted successfully'})
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== PATIENT VIEWS ====================

class PatientProfileView(APIView):
    """Patient profile management"""
    
    def get(self, request):
        if request.user.role != 'patient':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            patient = Patient.objects.get(user=request.user)
            serializer = PatientSerializer(patient)
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response({})
    
    def post(self, request):
        if request.user.role != 'patient':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        patient, created = Patient.objects.get_or_create(user=request.user)
        
        patient.full_name = data.get('full_name', '')
        patient.age = data.get('age', '')
        patient.marital_status = data.get('marital_status', '')
        patient.gender = data.get('gender', '')
        patient.address = data.get('address', '')
        patient.phone = data.get('phone', '')
        patient.email = data.get('email', '')
        patient.disease = data.get('disease', '')
        patient.save()
        
        return Response({'message': 'Profile saved successfully'})


class PatientAppointmentView(APIView):
    """Patient appointment management"""
    
    def post(self, request):
        if request.user.role != 'patient':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        doctor_username = data.get('doctor_username')
        
        doctor = None
        if doctor_username:
            try:
                doctor = User.objects.get(username=doctor_username, role='doctor')
            except User.DoesNotExist:
                pass
        
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            disease=data.get('disease', ''),
            appointment_date=data.get('appointment_date', None)
        )
        
        # Update patient status
        try:
            patient = Patient.objects.get(user=request.user)
            patient.status = 'appointment_pending'
            patient.save()
        except Patient.DoesNotExist:
            pass
        
        return Response({
            'message': 'Appointment requested successfully',
            'appointment_id': appointment.id
        })


# ==================== DOCTOR VIEWS ====================

class DoctorPatientsView(APIView):
    """Doctor patient management"""
    
    def get(self, request):
        if request.user.role != 'doctor':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        patients = Patient.objects.filter(doctor=request.user).select_related('user')
        data = {}
        for p in patients:
            data[p.user.username] = {
                'full_name': p.full_name,
                'age': p.age,
                'marital_status': p.marital_status,
                'gender': p.gender,
                'address': p.address,
                'phone': p.phone,
                'email': p.email,
                'disease': p.disease,
                'doctor': p.doctor.username if p.doctor else '',
                'status': p.status,
                'created_at': p.created_at.isoformat() if p.created_at else ''
            }
        return Response(data)


class DoctorPatientActionView(APIView):
    """Doctor patient actions - sign, discharge, delete"""
    
    def post(self, request, patient_username, action=None):
        if request.user.role != 'doctor':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            patient = Patient.objects.get(user__username=patient_username, doctor=request.user)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)
        
        if action == 'sign':
            patient.status = 'under_treatment'
            patient.save()
            return Response({'message': 'Patient signed successfully'})
        elif action == 'discharge':
            patient.status = 'discharged'
            patient.save()
            return Response({'message': 'Patient discharged successfully'})
        
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, patient_username):
        if request.user.role != 'doctor':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            patient = Patient.objects.get(user__username=patient_username, doctor=request.user)
            patient.user.delete()
            return Response({'message': 'Patient deleted successfully'})
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)


# ==================== MEDICAL RECORDS VIEWS ====================

class MedicalRecordView(APIView):
    """Medical records management"""
    
    def get(self, request):
        if request.user.role not in ['patient', 'doctor', 'admin']:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.role == 'patient':
            records = MedicalRecord.objects.filter(patient=request.user)
        elif request.user.role == 'doctor':
            records = MedicalRecord.objects.filter(doctor=request.user)
        else:
            records = MedicalRecord.objects.all()
        
        data = {}
        for r in records:
            data[r.id] = {
                'patient_username': r.patient.username,
                'doctor_username': r.doctor.username if r.doctor else '',
                'diagnosis': r.diagnosis,
                'treatment': r.treatment,
                'medications': r.medications,
                'notes': r.notes,
                'created_at': r.created_at.isoformat() if r.created_at else '',
                'updated_at': r.updated_at.isoformat() if r.updated_at else ''
            }
        return Response(data)
    
    def post(self, request):
        if request.user.role != 'doctor':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        patient_username = data.get('patient_username')
        
        if not patient_username:
            return Response({'error': 'patient_username required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(user__username=patient_username, doctor=request.user)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)
        
        record = MedicalRecord.objects.create(
            patient=patient.user,
            doctor=request.user,
            diagnosis=data.get('diagnosis', ''),
            treatment=data.get('treatment', ''),
            medications=data.get('medications', ''),
            notes=data.get('notes', '')
        )
        
        return Response({
            'message': 'Medical record created successfully',
            'record_id': record.id
        })


class MedicalRecordDetailView(APIView):
    """Medical record detail - update"""
    
    def put(self, request, record_id):
        if request.user.role != 'doctor':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        
        try:
            record = MedicalRecord.objects.get(id=record_id, doctor=request.user)
        except MedicalRecord.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'diagnosis' in data:
            record.diagnosis = data['diagnosis']
        if 'treatment' in data:
            record.treatment = data['treatment']
        if 'medications' in data:
            record.medications = data['medications']
        if 'notes' in data:
            record.notes = data['notes']
        
        record.save()
        
        return Response({'message': 'Medical record updated successfully'})


# ==================== APPOINTMENT VIEWS ====================

class AppointmentView(APIView):
    """Appointment list and creation"""
    
    def get(self, request):
        if request.user.role not in ['patient', 'doctor', 'admin']:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.role == 'patient':
            appointments = Appointment.objects.filter(patient=request.user)
        elif request.user.role == 'doctor':
            # Get patients assigned to this doctor
            patient_users = Patient.objects.filter(doctor=request.user).values_list('user', flat=True)
            appointments = Appointment.objects.filter(patient__in=patient_users)
        else:
            appointments = Appointment.objects.all()
        
        data = {}
        for a in appointments:
            data[a.id] = {
                'patient_username': a.patient.username,
                'doctor_username': a.doctor.username if a.doctor else '',
                'disease': a.disease,
                'status': a.status,
                'appointment_date': str(a.appointment_date) if a.appointment_date else '',
                'notes': a.notes,
                'created_at': a.created_at.isoformat() if a.created_at else '',
                'updated_at': a.updated_at.isoformat() if a.updated_at else ''
            }
        return Response(data)


class AppointmentCalendarView(APIView):
    """Appointment calendar view with date filtering"""
    
    def get(self, request):
        if request.user.role not in ['patient', 'doctor', 'admin']:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        start_date = request.query_params.get('start_date', '')
        end_date = request.query_params.get('end_date', '')
        
        if request.user.role == 'patient':
            appointments = Appointment.objects.filter(patient=request.user)
        elif request.user.role == 'doctor':
            patient_users = Patient.objects.filter(doctor=request.user).values_list('user', flat=True)
            appointments = Appointment.objects.filter(patient__in=patient_users)
        else:
            appointments = Appointment.objects.all()
        
        if start_date:
            appointments = appointments.filter(appointment_date__gte=start_date)
        if end_date:
            appointments = appointments.filter(appointment_date__lte=end_date)
        
        data = {}
        for a in appointments:
            data[a.id] = {
                'patient_username': a.patient.username,
                'doctor_username': a.doctor.username if a.doctor else '',
                'disease': a.disease,
                'status': a.status,
                'appointment_date': str(a.appointment_date) if a.appointment_date else '',
                'notes': a.notes,
                'created_at': a.created_at.isoformat() if a.created_at else '',
                'updated_at': a.updated_at.isoformat() if a.updated_at else ''
            }
        return Response(data)


class AppointmentDetailView(APIView):
    """Appointment detail - update"""
    
    def put(self, request, appointment_id):
        if request.user.role not in ['doctor', 'admin']:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'status' in data:
            appointment.status = data['status']
        if 'appointment_date' in data:
            appointment.appointment_date = data['appointment_date']
        if 'notes' in data:
            appointment.notes = data['notes']
        
        appointment.save()
        
        return Response({'message': 'Appointment updated successfully'})


# ==================== BILLING VIEWS ====================

class BillView(APIView):
    """Bill list and creation"""
    
    def get(self, request):
        if request.user.role not in ['patient', 'doctor', 'admin']:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.role == 'patient':
            bills = Bill.objects.filter(patient=request.user)
        elif request.user.role == 'doctor':
            bills = Bill.objects.filter(doctor=request.user)
        else:
            bills = Bill.objects.all()
        
        data = {}
        for b in bills:
            data[b.id] = {
                'patient_username': b.patient.username,
                'doctor_username': b.doctor.username if b.doctor else '',
                'bill_type': b.bill_type,
                'description': b.description,
                'amount': str(b.amount),
                'status': b.status,
                'due_date': str(b.due_date) if b.due_date else '',
                'created_at': b.created_at.isoformat() if b.created_at else '',
                'updated_at': b.updated_at.isoformat() if b.updated_at else ''
            }
        return Response(data)
    
    def post(self, request):
        if request.user.role not in ['doctor', 'admin']:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        patient_username = data.get('patient_username')
        
        if not patient_username:
            return Response({'error': 'patient_username required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = User.objects.get(username=patient_username, role='patient')
        except User.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        bill = Bill.objects.create(
            patient=patient,
            doctor=request.user if request.user.role == 'doctor' else None,
            bill_type=data.get('bill_type', 'consultation'),
            description=data.get('description', ''),
            amount=data.get('amount', 0),
            due_date=data.get('due_date', None)
        )
        
        # Create notification for patient
        Notification.objects.create(
            user=patient,
            notification_type='bill',
            title='New Bill Created',
            message=f'A new bill of ${bill.amount} has been created for you.'
        )
        
        return Response({
            'message': 'Bill created successfully',
            'bill_id': bill.id
        })


class BillDetailView(APIView):
    """Bill detail - update or delete"""
    
    def put(self, request, bill_id):
        if request.user.role not in ['doctor', 'admin']:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        
        try:
            bill = Bill.objects.get(id=bill_id)
        except Bill.DoesNotExist:
            return Response({'error': 'Bill not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'status' in data:
            bill.status = data['status']
        if 'amount' in data:
            bill.amount = data['amount']
        if 'due_date' in data:
            bill.due_date = data['due_date']
        if 'description' in data:
            bill.description = data['description']
        
        bill.save()
        
        return Response({'message': 'Bill updated successfully'})
    
    def delete(self, request, bill_id):
        if request.user.role != 'admin':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            bill = Bill.objects.get(id=bill_id)
            bill.delete()
            return Response({'message': 'Bill deleted successfully'})
        except Bill.DoesNotExist:
            return Response({'error': 'Bill not found'}, status=status.HTTP_404_NOT_FOUND)


class PaymentView(APIView):
    """Payment list and creation"""
    
    def get(self, request):
        if request.user.role not in ['patient', 'doctor', 'admin']:
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.role == 'patient':
            payments = Payment.objects.filter(patient=request.user)
        else:
            payments = Payment.objects.all()
        
        data = {}
        for p in payments:
            data[p.id] = {
                'bill_id': p.bill.id,
                'patient_username': p.patient.username,
                'amount': str(p.amount),
                'payment_method': p.payment_method,
                'status': p.status,
                'transaction_id': p.transaction_id,
                'notes': p.notes,
                'payment_date': p.payment_date.isoformat() if p.payment_date else ''
            }
        return Response(data)
    
    def post(self, request):
        if request.user.role != 'patient':
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data
        bill_id = data.get('bill_id')
        
        if not bill_id:
            return Response({'error': 'bill_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            bill = Bill.objects.get(id=bill_id, patient=request.user)
        except Bill.DoesNotExist:
            return Response({'error': 'Bill not found or not yours'}, status=status.HTTP_404_NOT_FOUND)
        
        payment = Payment.objects.create(
            bill=bill,
            patient=request.user,
            amount=data.get('amount', bill.amount),
            payment_method=data.get('payment_method', 'cash'),
            transaction_id=data.get('transaction_id', ''),
            notes=data.get('notes', ''),
            status='completed'
        )
        
        # Update bill status
        bill.status = 'paid'
        bill.save()
        
        return Response({
            'message': 'Payment successful',
            'payment_id': payment.id
        })


# ==================== NOTIFICATION VIEWS ====================

class NotificationView(APIView):
    """Notification list"""
    
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        data = {}
        for n in notifications:
            data[n.id] = {
                'notification_type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat() if n.created_at else ''
            }
        return Response(data)


class NotificationDetailView(APIView):
    """Mark notification as read"""
    
    def put(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            return Response({'message': 'Notification deleted'})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

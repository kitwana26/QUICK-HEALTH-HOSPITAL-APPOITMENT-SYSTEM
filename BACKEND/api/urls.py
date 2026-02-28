from django.urls import path
from . import views

urlpatterns = [
    # Auth endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Admin endpoints
    path('admin/doctors/', views.AdminDoctorView.as_view(), name='admin-doctors'),
    path('admin/doctors/<str:doctor_username>/', views.AdminDoctorDetailView.as_view(), name='admin-doctor-detail'),
    path('admin/patients/', views.AdminPatientView.as_view(), name='admin-patients'),
    path('admin/patients/<str:patient_username>/', views.AdminPatientDetailView.as_view(), name='admin-patient-detail'),
    
    # Patient endpoints
    path('patient/profile/', views.PatientProfileView.as_view(), name='patient-profile'),
    path('patient/appointment/', views.PatientAppointmentView.as_view(), name='patient-appointment'),
    
    # Doctor endpoints - using action parameter in URL
    path('doctor/patients/', views.DoctorPatientsView.as_view(), name='doctor-patients'),
    path('doctor/patients/<str:patient_username>/', views.DoctorPatientActionView.as_view(), name='doctor-patient-detail'),
    path('doctor/patients/<str:patient_username>/<str:action>/', views.DoctorPatientActionView.as_view(), name='doctor-patient-action'),
    
    # Medical records endpoints
    path('medical-records/', views.MedicalRecordView.as_view(), name='medical-records'),
    path('medical-records/<int:record_id>/', views.MedicalRecordDetailView.as_view(), name='medical-record-detail'),
    
    # Appointment endpoints
    path('appointments/', views.AppointmentView.as_view(), name='appointments'),
    path('appointments/calendar/', views.AppointmentCalendarView.as_view(), name='appointments-calendar'),
    path('appointments/<int:appointment_id>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    
    # Billing endpoints
    path('bills/', views.BillView.as_view(), name='bills'),
    path('bills/<int:bill_id>/', views.BillDetailView.as_view(), name='bill-detail'),
    
    # Payment endpoints
    path('payments/', views.PaymentView.as_view(), name='payments'),
    
    # Notification endpoints
    path('notifications/', views.NotificationView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/', views.NotificationDetailView.as_view(), name='notification-detail'),
]

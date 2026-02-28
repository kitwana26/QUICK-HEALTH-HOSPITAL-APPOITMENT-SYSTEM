from django.contrib import admin
from .models import User, Patient, Appointment, MedicalRecord

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role']
    list_filter = ['role']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'status', 'doctor']
    list_filter = ['status']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'status']
    list_filter = ['status']

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'created_at']

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """Custom User model with role field"""
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    token = models.CharField(max_length=64, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)


class Patient(models.Model):
    """Patient profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    full_name = models.CharField(max_length=200, blank=True, default='')
    age = models.CharField(max_length=10, blank=True, default='')
    marital_status = models.CharField(max_length=20, blank=True, default='')
    gender = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    disease = models.TextField(blank=True, default='')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_patients')
    status = models.CharField(max_length=20, default='pending')  # pending, appointment_pending, under_treatment, discharged
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    """Patient appointments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_appointments')
    disease = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    appointment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.username} - {self.appointment_date}"


class MedicalRecord(models.Model):
    """Medical records created by doctors"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_records')
    diagnosis = models.TextField(blank=True, default='')
    treatment = models.TextField(blank=True, default='')
    medications = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.username} - {self.created_at}"


# ==================== BILLING MODELS ====================

class Bill(models.Model):
    """Patient bills for services"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    BILL_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('treatment', 'Treatment'),
        ('medication', 'Medication'),
        ('lab_test', 'Lab Test'),
        ('room_charge', 'Room Charge'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bills')
    bill_type = models.CharField(max_length=20, choices=BILL_TYPE_CHOICES, default='consultation')
    description = models.TextField(blank=True, default='')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bill #{self.id} - {self.patient.username} - ${self.amount}"


class Payment(models.Model):
    """Payment records for bills"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('insurance', 'Insurance'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment #{self.id} - Bill #{self.bill.id} - ${self.amount}"


# ==================== NOTIFICATION MODELS ====================

class Notification(models.Model):
    """User notifications"""
    TYPE_CHOICES = [
        ('appointment', 'Appointment'),
        ('bill', 'Bill'),
        ('medical_record', 'Medical Record'),
        ('system', 'System'),
        ('message', 'Message'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.title} - {self.user.username}"

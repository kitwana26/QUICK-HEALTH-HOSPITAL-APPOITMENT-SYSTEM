from rest_framework import serializers
from .models import User, Patient, Appointment, MedicalRecord, Bill, Payment, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'token', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }


class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.CharField(source='user.first_name', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'username', 'full_name', 'age', 'marital_status', 'gender',
            'address', 'phone', 'email', 'disease', 'doctor', 'status',
            'created_at', 'name'
        ]
        read_only_fields = ['status', 'created_at']


class AppointmentSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    doctor_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_username', 'doctor_username', 'disease', 'status',
            'appointment_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status']
    
    def get_doctor_username(self, obj):
        return obj.doctor.username if obj.doctor else None


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    doctor_username = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient_username', 'doctor_username', 'diagnosis', 'treatment',
            'medications', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'doctor']
    
    def get_doctor_username(self, obj):
        return obj.doctor.username if obj.doctor else None


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role', 'name']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        name = validated_data.pop('name', '')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            role=validated_data.get('role', 'patient'),
            first_name=name,
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# ==================== BILLING SERIALIZERS ====================

class BillSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    doctor_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = [
            'id', 'patient_username', 'doctor_username', 'bill_type', 'description',
            'amount', 'status', 'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status']
    
    def get_doctor_username(self, obj):
        return obj.doctor.username if obj.doctor else None


class PaymentSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    bill_id = serializers.IntegerField(source='bill.id', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'bill_id', 'patient_username', 'amount', 'payment_method',
            'status', 'transaction_id', 'notes', 'payment_date'
        ]
        read_only_fields = ['payment_date', 'status']


# ==================== NOTIFICATION SERIALIZERS ====================

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'is_read', 'created_at'
        ]
        read_only_fields = ['created_at']

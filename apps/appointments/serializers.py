from django.utils import timezone
from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('id', 'title', 'doctor_name', 'location',
                  'appointment_date', 'notes', 'is_completed',
                  'reminder_days_before', 'created_at')
        read_only_fields = ('created_at',)

    def validate_appointment_date(self, value):
        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError(
                'Appointment date must be in the future.')
        return value

    def validate_reminder_days_before(self, value):
        if value < 0:
            raise serializers.ValidationError('reminder date must be greater than 0')
        return value
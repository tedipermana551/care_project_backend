from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    title = models.CharField(max_length=200)
    doctor_name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)
    appointment_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    reminder_days_before = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date']

    def __str__(self):
        return f'{self.title} - {self.doctor_name} ({self.appointment_date})'
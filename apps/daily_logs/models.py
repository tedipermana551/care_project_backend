from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DailyLog(models.Model):
    MOOD_CHOICES = [
        ('great', 'Great'),
        ('good', 'Good'),
        ('neutral', 'Neutral'),
        ('bad', 'Bad'),
        ('terrible', 'Terrible'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField(default=timezone.now)
    mood = models.CharField(choices=MOOD_CHOICES, max_length=10)
    complaints = models.TextField(blank=True)
    sleep_duration = models.DecimalField(max_digits=5, decimal_places=1, help_text='hours')
    exercise_duration = models.DecimalField(max_digits=5, decimal_places=1, help_text='minutes')
    notes = models.TextField(blank=True)
    partner_message = models.CharField(max_length=280, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ('-date',)

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.date} ({self.mood})'
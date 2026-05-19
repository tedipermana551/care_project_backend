import secrets
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = [('mother','Mother'),('husband','Husband')]

    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(choices=ROLE_CHOICES, max_length=10, blank=True)
    unique_code = models.CharField(max_length=10, unique=True, editable=False)
    partner = models.OneToOneField(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='partner_of'
    )
    due_date = models.DateField(null=True, blank=True)
    pregnancy_start_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'UserProfile'

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.role})'

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = self._generate_unique_code()
        super().save(*args, **kwargs)

    def clean(self):
        if self.role == 'mother' and self.due_date:
            if self.due_date <= timezone.now().date():
                raise ValidationError({'due_date': 'Due date must be in the future'})

    @staticmethod
    def _generate_unique_code():
        while True:
            code = secrets.token_urlsafe(6).upper()[:8]
            if not UserProfile.objects.filter(unique_code=code).exists():
                return code

    @property
    def mother_profile(self):
        if self.role == 'mother':
            return self
        if self.partner and self.partner.role == 'mother':
            return self.partner
        return None
import os
import secrets
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

def _avatar_upload_path(instance, filename):
    """
    Store avatars at:  media/avatars/<user_id>/<uuid>.<ext>

    Using uuid as the filename:
    - Prevents filename collisions when a user re-uploads
    - Avoids exposing the original filename in the URL
    - Makes old URLs immediately stale after a re-upload (old file
      has a different UUID name, so CDN/browser caches don't serve it)
    """
    ext = os.path.splitext(filename)[1].lower()  # e.g. ".jpg"
    new_name = f'{uuid.uuid4().hex}{ext}'
    return os.path.join('avatars', str(instance.user_id), new_name)

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
    # ── profile detail fields ──────────────────────────────────────────────────
    nickname = models.CharField(max_length=50, blank=True, default='')
    about = models.TextField(max_length=300, blank=True, default='')

    # null=True  → no DB column value when not uploaded (distinguishes "never
    #              uploaded" from "uploaded then deleted")
    # blank=True → field is optional in forms / serializers
    # upload_to  → routed through our helper so files land in
    #              MEDIA_ROOT/avatars/<user_id>/<uuid>.ext
    avatar = models.ImageField(
        upload_to=_avatar_upload_path,
        null=True,
        blank=True,
    )
    # ──────────────────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'UserProfile'

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.role})'

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = self._generate_unique_code()
        if self.pk:
            try:
                old = UserProfile.objects.get(pk=self.pk)
                if old.avatar and old.avatar != self.avatar:
                    old.avatar.delete(save=False)
            except UserProfile.DoesNotExist:
                pass
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
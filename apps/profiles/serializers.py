from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('id', 'full_name', 'email', 'role', 'unique_code','nickname', 'about',
            'avatar_url', 'due_date', 'pregnancy_start_date', 'created_at', 'updated_at')
        read_only_fields = ('unique_code', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_avatar_url(self, obj):
        """
        Return the full absolute URL for the avatar so the frontend
        never has to construct it manually.

        Returns None when no avatar has been uploaded — the frontend
        can fall back to initials or a default image.
        """
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        # Fallback: return the relative URL if no request in context
        return obj.avatar.url

class ProfileSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('role', 'due_date', 'pregnancy_start_date')

    def validate(self, data):
        role = data.get('role')
        due_date = data.get('due_date')
        if role == 'mother' and not due_date:
            raise serializers.ValidationError({'due_date': 'Due date is required for the mother role'})
        return data

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('due_date', 'pregnancy_start_date', 'nickname', 'about')

    def validate_nickname(self, value):
        return value.strip()

    def validate_about(self, value):
        return value.strip()


class AvatarUploadSerializer(serializers.ModelSerializer):
    """
    Used on PATCH /profile/avatar/ — accepts only the avatar field.

    Accepts multipart/form-data. Runs three validations:
      1. Must be an image MIME type (ImageField handles this via Pillow)
      2. Max file size: 2 MB
      3. Allowed extensions: jpg, jpeg, png, webp
    """
    avatar = serializers.ImageField(required=True)

    class Meta:
        model = UserProfile
        fields = ('avatar',)

    def validate_avatar(self, image):
        # ── size guard ────────────────────────────────────────────────────────
        max_bytes = 2 * 1024 * 1024  # 2 MB
        if image.size > max_bytes:
            raise serializers.ValidationError(
                f'Image size must not exceed 2 MB. '
                f'Uploaded file is {image.size / (1024 * 1024):.1f} MB.'
            )

        # ── extension guard ───────────────────────────────────────────────────
        import os
        allowed_exts = {'.jpg', '.jpeg', '.png', '.webp'}
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in allowed_exts:
            raise serializers.ValidationError(
                f'Unsupported file type "{ext}". '
                f'Allowed types: {", ".join(sorted(allowed_exts))}.'
            )

        return image


class AvatarDeleteSerializer(serializers.Serializer):
    """Empty serializer — DELETE /profile/avatar/ has no request body."""
    pass

# ── Minimal partner preview — shown inside daily log message responses ───
class PartnerPreviewSerializer(serializers.ModelSerializer):
    """Lightweight profile shown when a log message is read by the partner."""
    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('id', 'full_name', 'display_name', 'role', 'nickname', 'about', 'avatar_url')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_display_name(self, obj):
        return obj.nickname or (obj.user.get_full_name() or obj.user.username)

    def get_avatar_url(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url


# ─────────────────────────────────────────────────────────────────────────────

class LinkPartnerSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
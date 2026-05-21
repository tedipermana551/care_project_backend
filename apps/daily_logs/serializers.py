from rest_framework import serializers
from .models import DailyLog

class DailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLog
        fields = ('id', 'date', 'mood', 'complaints', 'sleep_duration',
                  'exercise_duration', 'notes','partner_message', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate_sleep_duration(self, value):
        if value < 0 or value > 24:
            raise serializers.ValidationError('Sleep_duration must be between 0 and 24 hours.')
        return value

    def validate_exercise_duration(self, value):
        if value < 0 or value > 1440:
            raise serializers.ValidationError('Exercise_duration must be between 0 and 1440 hours.')
        return value

    def validate_partner_message(self, value):
        return value.strip()


class PartnerLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for a partner viewing their linked user's logs.

    Intentionally exposes partner_message so the husband can read what
    the mother wrote. All fields are read-only from the partner's side —
    they can only view, not edit.

    Also hides nothing: the husband sees the full log so he can be
    informed and supportive.
    """
    # Nested sender info pulled from the log's user → userprofile
    sender_display_name = serializers.SerializerMethodField()
    sender_nickname = serializers.SerializerMethodField()
    has_message = serializers.SerializerMethodField()

    class Meta:
        model = DailyLog
        fields = (
            'id', 'date', 'mood', 'complaints',
            'sleep_duration', 'exercise_duration', 'notes',
            'partner_message',
            'has_message',
            'sender_display_name',
            'sender_nickname',
            'created_at', 'updated_at',
        )
        read_only_fields = fields  # everything is read-only for the partner

    def get_sender_display_name(self, obj):
        try:
            profile = obj.user.userprofile
            return profile.nickname or obj.user.get_full_name() or obj.user.username
        except Exception:
            return obj.user.get_full_name() or obj.user.username

    def get_sender_nickname(self, obj):
        try:
            return obj.user.userprofile.nickname or ''
        except Exception:
            return ''

    def get_has_message(self, obj):
        """Convenience bool so the frontend can highlight logs with messages."""
        return bool(obj.partner_message)
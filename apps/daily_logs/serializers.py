from rest_framework import serializers
from .models import DailyLog

class DailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLog
        fields = ('id', 'date', 'mood', 'complaints', 'sleep_duration',
                  'exercise_duration', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate_sleep_duration(self, value):
        if value < 0 or value > 24:
            raise serializers.ValidationError('Sleep_duration must be between 0 and 24 hours.')
        return value

    def validate_exercise_duration(self, value):
        if value < 0 or value > 1440:
            raise serializers.ValidationError('Exercise_duration must be between 0 and 1440 hours.')
        return value
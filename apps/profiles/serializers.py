from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('id', 'full_name', 'email', 'role', 'unique_code', 'due_date', 'pregnancy_start_date', 'created_at', 'updated_at')
        read_only_fields = ('unique_code', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

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
        fields = ('due_date', 'pregnancy_start_date')

class LinkPartnerSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
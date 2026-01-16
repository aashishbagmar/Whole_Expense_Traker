from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, FinancialData, UserPreference

User = get_user_model()

# backend/users/serializers.py

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_no']


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            'currency', 'theme',
            'notifications_enabled', 'email_alerts', 'push_alerts',
            'auto_backup', 'budget_notification', 'weekly_reports', 'monthly_analysis'
        ]

# backend/users/serializers.py

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'phone_no']

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        phone_no = validated_data.get('phone_no')

        user = User.objects.create_user(
            username=email,      # 🔥 CRITICAL FIX
            email=email,
            password=password
        )

        if phone_no:
            user.phone_no = phone_no
            user.save()

        return user






class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class FinancialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialData
        fields = '__all__'

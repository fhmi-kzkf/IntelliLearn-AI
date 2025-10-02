from rest_framework import serializers
from .models import User
from courses.models import Enrollment
from quizzes.models import QuizAttempt
from gamification.models import UserBadge


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    enrolled_courses_count = serializers.SerializerMethodField()
    completed_quizzes_count = serializers.SerializerMethodField()
    earned_badges_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'learning_level', 'bio', 'date_joined', 'last_login',
            'is_active', 'total_points', 'current_streak', 'enrolled_courses_count',
            'completed_quizzes_count', 'earned_badges_count'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'total_points', 'current_streak']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_enrolled_courses_count(self, obj):
        return Enrollment.objects.filter(user=obj).count()
    
    def get_completed_quizzes_count(self, obj):
        return QuizAttempt.objects.filter(user=obj, status='completed').count()
    
    def get_earned_badges_count(self, obj):
        return UserBadge.objects.filter(user=obj).count()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates"""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'learning_level', 'bio'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm',
            'learning_level'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
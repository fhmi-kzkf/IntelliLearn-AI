from rest_framework import serializers
from .models import Badge, UserBadge, PointTransaction, LearningStreak, Leaderboard
from accounts.models import User


class BadgeSerializer(serializers.ModelSerializer):
    """Serializer for Badge model"""
    earned_count = serializers.SerializerMethodField()
    rarity_display = serializers.CharField(source='get_rarity_display', read_only=True)
    badge_type_display = serializers.CharField(source='get_badge_type_display', read_only=True)
    
    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'description', 'icon', 'color', 'badge_type', 'badge_type_display',
            'rarity', 'rarity_display', 'points_value', 'requirement_description',
            'requirement_value', 'is_active', 'is_hidden', 'created_at', 'updated_at',
            'earned_count'
        ]
    
    def get_earned_count(self, obj):
        return obj.user_badges.count()


class UserBadgeSerializer(serializers.ModelSerializer):
    """Serializer for UserBadge model"""
    badge_name = serializers.CharField(source='badge.name', read_only=True)
    badge_icon = serializers.CharField(source='badge.icon', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserBadge
        fields = [
            'id', 'user', 'user_name', 'badge', 'badge_name', 'badge_icon', 'earned_at',
            'points_awarded'
        ]
        read_only_fields = ['user', 'earned_at', 'points_awarded']


class PointTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PointTransaction model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    
    class Meta:
        model = PointTransaction
        fields = [
            'id', 'user', 'user_name', 'transaction_type', 'transaction_type_display',
            'source', 'source_display', 'points', 'description', 'context_object_type',
            'context_object_id', 'balance_after', 'created_at'
        ]
        read_only_fields = ['user', 'balance_after', 'created_at']


class LearningStreakSerializer(serializers.ModelSerializer):
    """Serializer for LearningStreak model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = LearningStreak
        fields = [
            'id', 'user', 'user_name', 'current_streak', 'current_streak_start',
            'longest_streak', 'longest_streak_start', 'longest_streak_end',
            'last_activity_date', 'total_active_days', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for Leaderboard model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_learning_level = serializers.CharField(source='user.get_learning_level_display', read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'user', 'user_name', 'user_learning_level', 'metric', 'value',
            'period', 'rank', 'last_updated'
        ]
        read_only_fields = ['user', 'last_updated']
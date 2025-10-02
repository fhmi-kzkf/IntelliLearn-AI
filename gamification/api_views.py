from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from .models import Badge, UserBadge, PointTransaction, LearningStreak, Leaderboard
from .serializers import (
    BadgeSerializer, UserBadgeSerializer, PointTransactionSerializer, 
    LearningStreakSerializer, LeaderboardSerializer
)
from accounts.models import User


class BadgeListView(generics.ListAPIView):
    """API view for listing badges"""
    queryset = Badge.objects.filter(is_active=True).order_by('badge_type', 'name')
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class BadgeDetailView(generics.RetrieveAPIView):
    """API view for badge detail"""
    queryset = Badge.objects.filter(is_active=True)
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_badges(request):
    """API endpoint for user's earned badges"""
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge').order_by('-earned_at')
    serializer = UserBadgeSerializer(user_badges, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_badges(request):
    """API endpoint for badges not yet earned by user"""
    # Get IDs of badges user has already earned
    earned_badge_ids = UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True)
    
    # Get available badges
    available_badges = Badge.objects.filter(is_active=True).exclude(id__in=earned_badge_ids).order_by('badge_type', 'name')
    
    serializer = BadgeSerializer(available_badges, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def points_history(request):
    """API endpoint for user's points history"""
    transactions = PointTransaction.objects.filter(user=request.user).order_by('-created_at')
    serializer = PointTransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def learning_streak(request):
    """API endpoint for user's learning streak"""
    streak, created = LearningStreak.objects.get_or_create(user=request.user)
    serializer = LearningStreakSerializer(streak)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def leaderboard(request):
    """API endpoint for global leaderboard"""
    # Get top 50 users by total points
    top_users = User.objects.filter(is_active=True).order_by('-total_points')[:50]
    
    # Create leaderboard data
    leaderboard_data = []
    for i, user in enumerate(top_users, 1):
        leaderboard_data.append({
            'rank': i,
            'user_id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'total_points': user.total_points,
            'learning_level': user.get_learning_level_display()
        })
    
    return Response(leaderboard_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """API endpoint for user statistics"""
    user = request.user
    
    # Get user's stats
    stats = {
        'total_points': user.total_points,
        'current_streak': getattr(user, 'current_streak', 0),
        'earned_badges': UserBadge.objects.filter(user=user).count(),
        'completed_quizzes': user.quiz_attempts.filter(status='completed').count(),
        'enrolled_courses': user.enrollments.count(),
        'completed_courses': user.enrollments.filter(status='completed').count()
    }
    
    return Response(stats)
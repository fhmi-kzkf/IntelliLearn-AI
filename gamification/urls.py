from django.urls import path
from . import views
from . import api_views

app_name = 'gamification'

urlpatterns = [
    # Badges and achievements
    path('badges/', views.BadgeListView.as_view(), name='badges'),
    path('badges/<int:badge_id>/', views.BadgeDetailView.as_view(), name='badge_detail'),
    path('my-badges/', views.MyBadgesView.as_view(), name='my_badges'),
    
    # Points and transactions
    path('points/', views.PointsView.as_view(), name='points'),
    path('points/history/', views.PointsHistoryView.as_view(), name='points_history'),
    
    # Leaderboards
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('leaderboard/<str:metric>/', views.LeaderboardView.as_view(), name='leaderboard_metric'),
    path('leaderboard/<str:metric>/<str:period>/', views.LeaderboardView.as_view(), name='leaderboard_detail'),
    
    # Learning streaks
    path('streak/', views.StreakView.as_view(), name='streak'),
    path('streak/update/', views.UpdateStreakView.as_view(), name='update_streak'),
    
    # Achievement system
    path('achievements/', views.AchievementsView.as_view(), name='achievements'),
    path('achievements/check/', views.CheckAchievementsView.as_view(), name='check_achievements'),
    
    # API endpoints
    path('api/badges/', api_views.BadgeListView.as_view(), name='api_badges'),
    path('api/badges/<int:pk>/', api_views.BadgeDetailView.as_view(), name='api_badge_detail'),
    path('api/my-badges/', api_views.my_badges, name='api_my_badges'),
    path('api/badges/available/', api_views.available_badges, name='api_available_badges'),
    path('api/points/history/', api_views.points_history, name='api_points_history'),
    path('api/leaderboard/', api_views.leaderboard, name='api_leaderboard'),
    path('api/streak/', api_views.learning_streak, name='api_streak'),
    path('api/user/stats/', api_views.user_stats, name='api_user_stats'),
]
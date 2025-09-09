from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta


class Badge(models.Model):
    """Achievement badges for gamification"""
    
    TYPE_CHOICES = [
        ('completion', 'Course Completion'),
        ('streak', 'Learning Streak'),
        ('quiz', 'Quiz Performance'),
        ('participation', 'Participation'),
        ('special', 'Special Achievement'),
        ('milestone', 'Milestone'),
    ]
    
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    color = models.CharField(max_length=7, default='#E02424', help_text="Hex color code")
    
    # Badge properties
    badge_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    points_value = models.PositiveIntegerField(default=0, help_text="Points awarded when earned")
    
    # Requirements (stored as JSON or simple fields)
    requirement_description = models.TextField(help_text="Human-readable requirement description")
    requirement_value = models.PositiveIntegerField(default=1, help_text="Numeric requirement (e.g., courses to complete)")
    
    # Badge settings
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False, help_text="Hidden until earned")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_rarity_color(self):
        """Return color class for badge rarity"""
        colors = {
            'common': 'text-gray-500',
            'uncommon': 'text-green-500',
            'rare': 'text-blue-500',
            'epic': 'text-purple-500',
            'legendary': 'text-yellow-500',
        }
        return colors.get(self.rarity, 'text-gray-500')
    
    def earned_count(self):
        """Count how many users have earned this badge"""
        return self.user_badges.count()
    
    class Meta:
        db_table = 'badges'
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'
        ordering = ['badge_type', 'name']


class UserBadge(models.Model):
    """Track badges earned by users"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    
    # Achievement details
    earned_at = models.DateTimeField(auto_now_add=True)
    points_awarded = models.PositiveIntegerField(default=0)
    
    # Optional context
    context_object_type = models.CharField(max_length=50, blank=True, help_text="Type of object that triggered the badge")
    context_object_id = models.PositiveIntegerField(blank=True, null=True, help_text="ID of object that triggered the badge")
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
    
    class Meta:
        db_table = 'user_badges'
        verbose_name = 'User Badge'
        verbose_name_plural = 'User Badges'
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']


class PointTransaction(models.Model):
    """Track all point transactions for users"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('earned', 'Points Earned'),
        ('spent', 'Points Spent'),
        ('bonus', 'Bonus Points'),
        ('penalty', 'Penalty'),
        ('adjustment', 'Manual Adjustment'),
    ]
    
    SOURCE_CHOICES = [
        ('quiz_completion', 'Quiz Completion'),
        ('course_completion', 'Course Completion'),
        ('lesson_completion', 'Lesson Completion'),
        ('streak_bonus', 'Streak Bonus'),
        ('badge_earned', 'Badge Earned'),
        ('daily_login', 'Daily Login'),
        ('admin_adjustment', 'Admin Adjustment'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='point_transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    points = models.IntegerField(help_text="Positive for earned, negative for spent")
    description = models.CharField(max_length=200)
    
    # Context (what triggered this transaction)
    context_object_type = models.CharField(max_length=50, blank=True)
    context_object_id = models.PositiveIntegerField(blank=True, null=True)
    
    # Balance after this transaction
    balance_after = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.points} points ({self.source})"
    
    class Meta:
        db_table = 'point_transactions'
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'
        ordering = ['-created_at']


class LearningStreak(models.Model):
    """Track learning streaks for users"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_streak')
    
    # Current streak
    current_streak = models.PositiveIntegerField(default=0)
    current_streak_start = models.DateField(blank=True, null=True)
    
    # Best streak
    longest_streak = models.PositiveIntegerField(default=0)
    longest_streak_start = models.DateField(blank=True, null=True)
    longest_streak_end = models.DateField(blank=True, null=True)
    
    # Tracking
    last_activity_date = models.DateField(blank=True, null=True)
    total_active_days = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} day streak"
    
    def update_streak(self, activity_date=None):
        """Update streak based on activity"""
        if activity_date is None:
            activity_date = timezone.now().date()
        
        # If first activity
        if not self.last_activity_date:
            self.current_streak = 1
            self.current_streak_start = activity_date
            self.last_activity_date = activity_date
            self.total_active_days = 1
        else:
            # Check if activity is consecutive
            days_diff = (activity_date - self.last_activity_date).days
            
            if days_diff == 1:  # Consecutive day
                self.current_streak += 1
                self.total_active_days += 1
            elif days_diff == 0:  # Same day, no change
                pass
            else:  # Streak broken
                # Check if current streak is the longest
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
                    self.longest_streak_start = self.current_streak_start
                    self.longest_streak_end = self.last_activity_date
                
                # Reset current streak
                self.current_streak = 1
                self.current_streak_start = activity_date
                self.total_active_days += 1
            
            self.last_activity_date = activity_date
        
        # Update longest streak if current is longer
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
            self.longest_streak_start = self.current_streak_start
            self.longest_streak_end = activity_date
        
        self.save()
        return self.current_streak
    
    def check_streak_broken(self):
        """Check if streak should be broken due to inactivity"""
        if self.last_activity_date:
            days_since_last = (timezone.now().date() - self.last_activity_date).days
            if days_since_last > 1:
                # Streak is broken
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
                    self.longest_streak_start = self.current_streak_start
                    self.longest_streak_end = self.last_activity_date
                
                self.current_streak = 0
                self.current_streak_start = None
                self.save()
                return True
        return False
    
    class Meta:
        db_table = 'learning_streaks'
        verbose_name = 'Learning Streak'
        verbose_name_plural = 'Learning Streaks'


class Leaderboard(models.Model):
    """Leaderboard rankings for different metrics"""
    
    METRIC_CHOICES = [
        ('total_points', 'Total Points'),
        ('courses_completed', 'Courses Completed'),
        ('quiz_average', 'Quiz Average Score'),
        ('current_streak', 'Current Learning Streak'),
        ('badges_earned', 'Badges Earned'),
    ]
    
    PERIOD_CHOICES = [
        ('all_time', 'All Time'),
        ('monthly', 'This Month'),
        ('weekly', 'This Week'),
        ('daily', 'Today'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leaderboard_entries')
    metric = models.CharField(max_length=30, choices=METRIC_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    
    # Ranking details
    rank = models.PositiveIntegerField()
    value = models.FloatField(help_text="The metric value (points, courses, etc.)")
    
    # Timestamps
    calculated_at = models.DateTimeField(auto_now_add=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    def __str__(self):
        return f"{self.user.username} - #{self.rank} in {self.get_metric_display()} ({self.get_period_display()})"
    
    class Meta:
        db_table = 'leaderboards'
        verbose_name = 'Leaderboard Entry'
        verbose_name_plural = 'Leaderboard Entries'
        unique_together = ['user', 'metric', 'period']
        ordering = ['metric', 'period', 'rank']

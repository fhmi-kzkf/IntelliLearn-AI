from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Badge, UserBadge, PointTransaction, LearningStreak, Leaderboard


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin for Badges"""
    
    list_display = (
        'name', 'badge_type_badge', 'rarity_badge', 'points_value',
        'earned_count_display', 'is_active', 'is_hidden', 'created_at'
    )
    list_filter = (
        'badge_type', 'rarity', 'is_active', 'is_hidden', 'created_at'
    )
    search_fields = ('name', 'description', 'requirement_description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon', 'color')
        }),
        ('Badge Properties', {
            'fields': ('badge_type', 'rarity', 'points_value')
        }),
        ('Requirements', {
            'fields': ('requirement_description', 'requirement_value')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_hidden')
        }),
    )
    
    def badge_type_badge(self, obj):
        colors = {
            'completion': 'green',
            'streak': 'blue',
            'quiz': 'orange',
            'participation': 'purple',
            'special': 'red',
            'milestone': 'yellow'
        }
        color = colors.get(obj.badge_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_badge_type_display()
        )
    badge_type_badge.short_description = 'Type'
    
    def rarity_badge(self, obj):
        colors = {
            'common': 'gray',
            'uncommon': 'green',
            'rare': 'blue',
            'epic': 'purple',
            'legendary': 'gold'
        }
        color = colors.get(obj.rarity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_rarity_display()
        )
    rarity_badge.short_description = 'Rarity'
    
    def earned_count_display(self, obj):
        count = obj.earned_count()
        return format_html(
            '<strong>{}</strong> user{}'.format(count, 's' if count != 1 else '')
        )
    earned_count_display.short_description = 'Earned By'


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """Admin for User Badges"""
    
    list_display = (
        'user', 'badge', 'badge_rarity', 'points_awarded',
        'earned_at', 'context_info'
    )
    list_filter = (
        'badge__badge_type', 'badge__rarity', 'earned_at'
    )
    search_fields = ('user__username', 'badge__name')
    readonly_fields = ('earned_at', 'points_awarded')
    
    fieldsets = (
        ('Badge Award', {
            'fields': ('user', 'badge', 'points_awarded')
        }),
        ('Context', {
            'fields': ('context_object_type', 'context_object_id')
        }),
        ('Timestamp', {
            'fields': ('earned_at',)
        }),
    )
    
    def badge_rarity(self, obj):
        return obj.badge.get_rarity_display()
    badge_rarity.short_description = 'Rarity'
    
    def context_info(self, obj):
        if obj.context_object_type and obj.context_object_id:
            return f"{obj.context_object_type} #{obj.context_object_id}"
        return "-"
    context_info.short_description = 'Context'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'badge')


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    """Admin for Point Transactions"""
    
    list_display = (
        'user', 'transaction_type_badge', 'source_badge', 'points',
        'balance_after', 'description', 'created_at'
    )
    list_filter = (
        'transaction_type', 'source', 'created_at'
    )
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at', 'balance_after')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'transaction_type', 'source', 'points', 'description')
        }),
        ('Context', {
            'fields': ('context_object_type', 'context_object_id')
        }),
        ('Result', {
            'fields': ('balance_after',)
        }),
    )
    
    def transaction_type_badge(self, obj):
        colors = {
            'earned': 'green',
            'spent': 'red',
            'bonus': 'blue',
            'penalty': 'orange',
            'adjustment': 'purple'
        }
        color = colors.get(obj.transaction_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_transaction_type_display()
        )
    transaction_type_badge.short_description = 'Type'
    
    def source_badge(self, obj):
        colors = {
            'quiz_completion': 'blue',
            'course_completion': 'green',
            'lesson_completion': 'lightblue',
            'streak_bonus': 'orange',
            'badge_earned': 'purple',
            'daily_login': 'yellow',
            'admin_adjustment': 'red'
        }
        color = colors.get(obj.source, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_source_display()
        )
    source_badge.short_description = 'Source'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(LearningStreak)
class LearningStreakAdmin(admin.ModelAdmin):
    """Admin for Learning Streaks"""
    
    list_display = (
        'user', 'current_streak_display', 'longest_streak_display',
        'total_active_days', 'last_activity_date', 'updated_at'
    )
    list_filter = ('last_activity_date', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = (
        'created_at', 'updated_at', 'total_active_days'
    )
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Current Streak', {
            'fields': (
                'current_streak', 'current_streak_start', 'last_activity_date'
            )
        }),
        ('Best Streak', {
            'fields': (
                'longest_streak', 'longest_streak_start', 'longest_streak_end'
            )
        }),
        ('Statistics', {
            'fields': ('total_active_days',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_streak_display(self, obj):
        if obj.current_streak > 0:
            color = 'green' if obj.current_streak >= 7 else 'blue' if obj.current_streak >= 3 else 'orange'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">{} days</span>',
                color, obj.current_streak
            )
        return format_html('<span style="color: gray;">No streak</span>')
    current_streak_display.short_description = 'Current Streak'
    
    def longest_streak_display(self, obj):
        if obj.longest_streak > 0:
            return format_html(
                '<span style="background-color: gold; color: black; padding: 2px 6px; border-radius: 3px; font-weight: bold;">{} days</span>',
                obj.longest_streak
            )
        return format_html('<span style="color: gray;">0 days</span>')
    longest_streak_display.short_description = 'Best Streak'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    """Admin for Leaderboard Entries"""
    
    list_display = (
        'user', 'metric_badge', 'period_badge', 'rank_display',
        'value', 'calculated_at'
    )
    list_filter = ('metric', 'period', 'calculated_at')
    search_fields = ('user__username',)
    readonly_fields = ('calculated_at',)
    
    fieldsets = (
        ('Leaderboard Entry', {
            'fields': ('user', 'metric', 'period')
        }),
        ('Ranking', {
            'fields': ('rank', 'value')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end', 'calculated_at')
        }),
    )
    
    def metric_badge(self, obj):
        colors = {
            'total_points': 'blue',
            'courses_completed': 'green',
            'quiz_average': 'orange',
            'current_streak': 'purple',
            'badges_earned': 'yellow'
        }
        color = colors.get(obj.metric, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_metric_display()
        )
    metric_badge.short_description = 'Metric'
    
    def period_badge(self, obj):
        colors = {
            'all_time': 'black',
            'monthly': 'blue',
            'weekly': 'green',
            'daily': 'orange'
        }
        color = colors.get(obj.period, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_period_display()
        )
    period_badge.short_description = 'Period'
    
    def rank_display(self, obj):
        colors = ['gold', 'silver', '#CD7F32']  # Bronze color
        if obj.rank <= 3:
            color = colors[obj.rank - 1]
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">#{}</span>',
                color, obj.rank
            )
        return f"#{obj.rank}"
    rank_display.short_description = 'Rank'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

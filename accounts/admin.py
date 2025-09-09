from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'role', 'learning_level', 'total_points', 'current_streak',
        'is_active', 'date_joined'
    )
    list_filter = (
        'role', 'learning_level', 'is_active', 'is_staff', 
        'date_joined', 'last_login'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('IntelliLearn Profile', {
            'fields': (
                'role', 'learning_level', 'bio', 'profile_picture',
                'date_of_birth', 'phone_number', 'preferred_learning_time'
            )
        }),
        ('Gamification', {
            'fields': (
                'total_points', 'current_streak', 'longest_streak', 
                'last_activity_date'
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('IntelliLearn Profile', {
            'fields': ('role', 'learning_level')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')
    
    def role_badge(self, obj):
        colors = {
            'learner': 'blue',
            'mentor': 'green', 
            'admin': 'red'
        }
        color = colors.get(obj.role, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    def level_badge(self, obj):
        colors = {
            'beginner': 'green',
            'intermediate': 'orange',
            'advanced': 'red'
        }
        color = colors.get(obj.learning_level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_learning_level_display()
        )
    level_badge.short_description = 'Level'


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    
    fieldsets = (
        ('Learning Preferences', {
            'fields': ('learning_goals', 'interests')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'push_notifications', 'weekly_digest')
        }),
        ('Privacy', {
            'fields': ('is_public_profile', 'show_progress')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    
    list_display = (
        'user', 'is_public_profile', 'show_progress', 
        'email_notifications', 'created_at'
    )
    list_filter = (
        'is_public_profile', 'show_progress', 'email_notifications',
        'push_notifications', 'weekly_digest'
    )
    search_fields = ('user__username', 'user__email', 'learning_goals')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Learning Information', {
            'fields': ('learning_goals', 'interests')
        }),
        ('Notification Preferences', {
            'fields': (
                'email_notifications', 'push_notifications', 
                'weekly_digest'
            )
        }),
        ('Privacy Settings', {
            'fields': ('is_public_profile', 'show_progress')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

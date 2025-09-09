from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import (
    AITutorSession, AITutorMessage, AIGeneratedContent, 
    PersonalizedRecommendation
)


class AITutorMessageInline(admin.TabularInline):
    """Inline admin for AI Tutor Messages"""
    model = AITutorMessage
    extra = 0
    readonly_fields = ('created_at', 'total_tokens')
    fields = (
        'sender', 'message_type', 'content', 'was_helpful', 'created_at'
    )
    ordering = ('created_at',)
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AITutorSession)
class AITutorSessionAdmin(admin.ModelAdmin):
    """Admin for AI Tutor Sessions"""
    
    list_display = (
        'user', 'title_display', 'context_type_badge', 'status_badge',
        'total_messages', 'satisfaction_display', 'duration_display',
        'started_at'
    )
    list_filter = (
        'context_type', 'status', 'user_satisfaction', 'started_at'
    )
    search_fields = ('user__username', 'title', 'session_id')
    readonly_fields = (
        'session_id', 'total_messages', 'started_at', 'ended_at', 'last_activity'
    )
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'session_id', 'title', 'status')
        }),
        ('Context', {
            'fields': (
                'context_type', 'context_object_type', 'context_object_id'
            )
        }),
        ('Metrics', {
            'fields': ('total_messages', 'user_satisfaction')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'ended_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AITutorMessageInline]
    
    def title_display(self, obj):
        return obj.title or f"Session {obj.session_id[:8]}..."
    title_display.short_description = 'Title'
    
    def context_type_badge(self, obj):
        colors = {
            'general': 'blue',
            'course': 'green',
            'quiz': 'orange',
            'concept': 'purple',
            'troubleshooting': 'red'
        }
        color = colors.get(obj.context_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_context_type_display()
        )
    context_type_badge.short_description = 'Context'
    
    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'ended': 'gray',
            'paused': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def satisfaction_display(self, obj):
        if obj.user_satisfaction:
            stars = '★' * obj.user_satisfaction + '☆' * (5 - obj.user_satisfaction)
            color = 'green' if obj.user_satisfaction >= 4 else 'orange' if obj.user_satisfaction >= 3 else 'red'
            return format_html(
                '<span style="color: {};">{}</span>',
                color, stars
            )
        return "-"
    satisfaction_display.short_description = 'Satisfaction'
    
    def duration_display(self, obj):
        duration = obj.get_duration()
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AITutorMessage)
class AITutorMessageAdmin(admin.ModelAdmin):
    """Admin for AI Tutor Messages"""
    
    list_display = (
        'session', 'sender_badge', 'message_type_badge', 'content_preview',
        'was_helpful_display', 'token_usage', 'created_at'
    )
    list_filter = (
        'sender', 'message_type', 'was_helpful', 'ai_model', 'created_at'
    )
    search_fields = ('content', 'session__title', 'session__user__username')
    readonly_fields = (
        'created_at', 'prompt_tokens', 'completion_tokens', 'total_tokens'
    )
    
    fieldsets = (
        ('Message Information', {
            'fields': ('session', 'sender', 'message_type')
        }),
        ('Content', {
            'fields': ('content', 'formatted_content')
        }),
        ('AI Metadata', {
            'fields': (
                'ai_model', 'prompt_tokens', 'completion_tokens', 'total_tokens'
            ),
            'classes': ('collapse',)
        }),
        ('User Feedback', {
            'fields': ('was_helpful', 'user_feedback')
        }),
    )
    
    def sender_badge(self, obj):
        colors = {
            'user': 'blue',
            'ai': 'green',
            'system': 'gray'
        }
        color = colors.get(obj.sender, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_sender_display()
        )
    sender_badge.short_description = 'Sender'
    
    def message_type_badge(self, obj):
        colors = {
            'text': 'blue',
            'code': 'green',
            'explanation': 'purple',
            'suggestion': 'orange',
            'feedback': 'yellow',
            'quiz_hint': 'red'
        }
        color = colors.get(obj.message_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_message_type_display()
        )
    message_type_badge.short_description = 'Type'
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def was_helpful_display(self, obj):
        if obj.was_helpful is True:
            return format_html('<span style="color: green;">✓ Helpful</span>')
        elif obj.was_helpful is False:
            return format_html('<span style="color: red;">✗ Not Helpful</span>')
        return "-"
    was_helpful_display.short_description = 'Helpful?'
    
    def token_usage(self, obj):
        if obj.total_tokens > 0:
            return f"{obj.total_tokens} tokens"
        return "-"
    token_usage.short_description = 'Tokens'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session__user')


@admin.register(AIGeneratedContent)
class AIGeneratedContentAdmin(admin.ModelAdmin):
    """Admin for AI Generated Content"""
    
    list_display = (
        'title', 'content_type_badge', 'status_badge', 'target_level_badge',
        'quality_score_display', 'human_rating_display', 'usage_count',
        'created_at'
    )
    list_filter = (
        'content_type', 'status', 'target_level', 'ai_model',
        'human_rating', 'created_at'
    )
    search_fields = ('title', 'content', 'prompt')
    readonly_fields = (
        'created_at', 'updated_at', 'usage_count', 'last_used'
    )
    
    fieldsets = (
        ('Content Information', {
            'fields': ('content_type', 'title', 'content')
        }),
        ('Generation Details', {
            'fields': ('prompt', 'ai_model', 'generation_parameters')
        }),
        ('Metadata', {
            'fields': ('target_level', 'topic_tags')
        }),
        ('Review Process', {
            'fields': ('status', 'created_by', 'reviewed_by')
        }),
        ('Quality Metrics', {
            'fields': ('quality_score', 'human_rating')
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'last_used'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_type_badge(self, obj):
        colors = {
            'quiz_question': 'blue',
            'course_material': 'green',
            'explanation': 'purple',
            'example': 'orange',
            'exercise': 'red',
            'feedback': 'yellow'
        }
        color = colors.get(obj.content_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_content_type_display()
        )
    content_type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'review': 'orange',
            'approved': 'blue',
            'published': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def target_level_badge(self, obj):
        if obj.target_level:
            colors = {
                'beginner': 'green',
                'intermediate': 'orange',
                'advanced': 'red'
            }
            color = colors.get(obj.target_level, 'gray')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                color, obj.target_level.title()
            )
        return "-"
    target_level_badge.short_description = 'Level'
    
    def quality_score_display(self, obj):
        if obj.quality_score is not None:
            percentage = obj.quality_score * 100
            color = 'green' if percentage >= 80 else 'orange' if percentage >= 60 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, percentage
            )
        return "-"
    quality_score_display.short_description = 'Quality'
    
    def human_rating_display(self, obj):
        if obj.human_rating:
            stars = '★' * obj.human_rating + '☆' * (5 - obj.human_rating)
            color = 'green' if obj.human_rating >= 4 else 'orange' if obj.human_rating >= 3 else 'red'
            return format_html(
                '<span style="color: {};">{}</span>',
                color, stars
            )
        return "-"
    human_rating_display.short_description = 'Rating'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'created_by', 'reviewed_by'
        )


@admin.register(PersonalizedRecommendation)
class PersonalizedRecommendationAdmin(admin.ModelAdmin):
    """Admin for Personalized Recommendations"""
    
    list_display = (
        'user', 'title', 'recommendation_type_badge', 'status_badge',
        'priority_display', 'confidence_score_display', 'created_at'
    )
    list_filter = (
        'recommendation_type', 'status', 'priority', 'created_at'
    )
    search_fields = ('user__username', 'title', 'description')
    readonly_fields = (
        'created_at', 'updated_at', 'viewed_at', 'responded_at'
    )
    
    fieldsets = (
        ('Recommendation Information', {
            'fields': (
                'user', 'recommendation_type', 'title', 'description', 'reason'
            )
        }),
        ('Target Content', {
            'fields': ('target_object_type', 'target_object_id')
        }),
        ('AI Details', {
            'fields': ('confidence_score', 'based_on_data')
        }),
        ('User Interaction', {
            'fields': ('status', 'viewed_at', 'responded_at')
        }),
        ('Settings', {
            'fields': ('priority', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def recommendation_type_badge(self, obj):
        colors = {
            'course': 'blue',
            'topic': 'green',
            'review': 'orange',
            'practice': 'purple',
            'path': 'red'
        }
        color = colors.get(obj.recommendation_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_recommendation_type_display()
        )
    recommendation_type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'viewed': 'blue',
            'accepted': 'green',
            'dismissed': 'red',
            'completed': 'darkgreen'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_display(self, obj):
        color = 'red' if obj.priority <= 3 else 'orange' if obj.priority <= 6 else 'green'
        priority_text = 'High' if obj.priority <= 3 else 'Medium' if obj.priority <= 6 else 'Low'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, priority_text
        )
    priority_display.short_description = 'Priority'
    
    def confidence_score_display(self, obj):
        percentage = obj.confidence_score * 100
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 60 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    confidence_score_display.short_description = 'Confidence'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

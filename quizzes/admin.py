from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceInline(admin.TabularInline):
    """Inline admin for Question Choices"""
    model = Choice
    extra = 4
    fields = ('text', 'is_correct', 'order', 'explanation')
    ordering = ('order',)


class QuestionInline(admin.StackedInline):
    """Inline admin for Quiz Questions"""
    model = Question
    extra = 1
    fields = (
        'question_type', 'text', 'explanation', 'code_snippet',
        'order', 'points', 'ai_generated'
    )
    ordering = ('order',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin for Quizzes"""
    
    list_display = (
        'title', 'course', 'difficulty_badge', 'source_badge',
        'question_count', 'attempt_count', 'average_score',
        'is_active', 'created_at'
    )
    list_filter = (
        'difficulty', 'source', 'is_active', 'course__category',
        'created_at'
    )
    search_fields = ('title', 'description', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course', 'lesson')
        }),
        ('Quiz Settings', {
            'fields': (
                'difficulty', 'time_limit', 'max_attempts',
                'shuffle_questions', 'show_correct_answers'
            )
        }),
        ('Content Source', {
            'fields': ('source', 'created_by')
        }),
        ('Gamification', {
            'fields': ('points_per_question', 'bonus_points')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuestionInline]
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'
    
    def attempt_count(self, obj):
        return obj.attempts.count()
    attempt_count.short_description = 'Attempts'
    
    def average_score(self, obj):
        avg_score = obj.attempts.filter(status='completed').aggregate(
            avg_score=Avg('percentage')
        )['avg_score']
        if avg_score:
            return f"{avg_score:.1f}%"
        return "-"
    average_score.short_description = 'Avg Score'
    
    def difficulty_badge(self, obj):
        colors = {
            'easy': 'green',
            'medium': 'orange',
            'hard': 'red'
        }
        color = colors.get(obj.difficulty, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_difficulty_display()
        )
    difficulty_badge.short_description = 'Difficulty'
    
    def source_badge(self, obj):
        colors = {
            'manual': 'blue',
            'ai_generated': 'purple',
            'hybrid': 'green'
        }
        color = colors.get(obj.source, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_source_display()
        )
    source_badge.short_description = 'Source'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'course', 'lesson', 'created_by'
        ).prefetch_related('questions', 'attempts')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin for Quiz Questions"""
    
    list_display = (
        'quiz', 'text_preview', 'question_type_badge', 'points',
        'order', 'ai_generated', 'created_at'
    )
    list_filter = (
        'question_type', 'ai_generated', 'quiz__difficulty',
        'created_at'
    )
    search_fields = ('text', 'explanation', 'quiz__title')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('quiz', 'question_type', 'text', 'explanation')
        }),
        ('Content', {
            'fields': ('code_snippet',)
        }),
        ('Settings', {
            'fields': ('order', 'points')
        }),
        ('AI Generation', {
            'fields': ('ai_generated', 'ai_prompt'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ChoiceInline]
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'
    
    def question_type_badge(self, obj):
        colors = {
            'multiple_choice': 'blue',
            'true_false': 'green',
            'fill_blank': 'orange',
            'short_answer': 'purple',
            'code_completion': 'red'
        }
        color = colors.get(obj.question_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_question_type_display()
        )
    question_type_badge.short_description = 'Type'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """Admin for Question Choices"""
    
    list_display = (
        'question', 'text_preview', 'is_correct', 'order'
    )
    list_filter = ('is_correct', 'question__question_type')
    search_fields = ('text', 'question__text')
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Choice Text'


class AnswerInline(admin.TabularInline):
    """Inline admin for Quiz Answers"""
    model = Answer
    extra = 0
    readonly_fields = ('question', 'is_correct', 'points_earned', 'answered_at')
    fields = ('question', 'selected_choice', 'text_answer', 'is_correct', 'points_earned')
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """Admin for Quiz Attempts"""
    
    list_display = (
        'user', 'quiz', 'attempt_number', 'status_badge',
        'score_display', 'percentage_bar', 'time_taken_display',
        'started_at'
    )
    list_filter = (
        'status', 'quiz__difficulty', 'quiz__course__category',
        'started_at', 'completed_at'
    )
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = (
        'score', 'percentage', 'started_at', 'completed_at',
        'time_taken', 'attempt_number'
    )
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('user', 'quiz', 'attempt_number', 'status')
        }),
        ('Results', {
            'fields': ('score', 'percentage')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'time_taken')
        }),
    )
    
    inlines = [AnswerInline]
    
    def status_badge(self, obj):
        colors = {
            'in_progress': 'blue',
            'completed': 'green',
            'time_expired': 'orange',
            'abandoned': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def score_display(self, obj):
        total_possible = obj.quiz.get_total_points()
        return f"{obj.score}/{total_possible}"
    score_display.short_description = 'Score'
    
    def percentage_bar(self, obj):
        percentage = obj.percentage
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 60 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px; overflow: hidden;">' +
            '<div style="width: {}%; height: 20px; background-color: {}; text-align: center; color: white; font-size: 11px; line-height: 20px;">' +
            '{}%</div></div>',
            percentage, color, int(percentage)
        )
    percentage_bar.short_description = 'Score %'
    
    def time_taken_display(self, obj):
        if obj.time_taken:
            total_seconds = int(obj.time_taken.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"
    time_taken_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'quiz'
        ).prefetch_related('answers')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin for Quiz Answers"""
    
    list_display = (
        'attempt', 'question', 'is_correct', 'points_earned',
        'ai_evaluated', 'answered_at'
    )
    list_filter = (
        'is_correct', 'ai_evaluated', 'question__question_type',
        'answered_at'
    )
    search_fields = (
        'attempt__user__username', 'question__text', 'text_answer'
    )
    readonly_fields = ('answered_at',)
    
    fieldsets = (
        ('Answer Information', {
            'fields': ('attempt', 'question')
        }),
        ('Response', {
            'fields': ('selected_choice', 'text_answer')
        }),
        ('Evaluation', {
            'fields': ('is_correct', 'points_earned', 'ai_evaluated', 'ai_feedback')
        }),
    )

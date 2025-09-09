from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Course, Lesson, Enrollment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Course Categories"""
    
    list_display = (
        'name', 'course_count', 'color_preview', 'icon_preview', 
        'order', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Appearance', {
            'fields': ('icon', 'color')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Courses'
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
        return '-'
    icon_preview.short_description = 'Icon'


class LessonInline(admin.TabularInline):
    """Inline admin for Lessons"""
    model = Lesson
    extra = 1
    fields = ('title', 'content_type', 'estimated_reading_time', 'order', 'is_free')
    ordering = ('order',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin for Courses"""
    
    list_display = (
        'title', 'category', 'instructor', 'level_badge', 'status_badge',
        'lesson_count', 'enrollment_count', 'points_reward', 'created_at'
    )
    list_filter = (
        'level', 'status', 'category', 'created_at', 'published_at'
    )
    search_fields = ('title', 'description', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('prerequisites',)
    readonly_fields = ('view_count', 'enrollment_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'slug', 'description', 'short_description',
                'thumbnail'
            )
        }),
        ('Course Organization', {
            'fields': (
                'category', 'level', 'prerequisites', 'instructor'
            )
        }),
        ('Settings', {
            'fields': (
                'status', 'estimated_duration', 'points_reward', 'order'
            )
        }),
        ('Statistics', {
            'fields': ('view_count', 'enrollment_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [LessonInline]
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'
    
    def level_badge(self, obj):
        colors = {
            'beginner': 'green',
            'intermediate': 'orange',
            'advanced': 'red'
        }
        color = colors.get(obj.level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_level_display()
        )
    level_badge.short_description = 'Level'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'published': 'green',
            'archived': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'instructor'
        ).prefetch_related('lessons')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin for Lessons"""
    
    list_display = (
        'title', 'course', 'content_type_badge', 'estimated_reading_time',
        'order', 'is_free', 'created_at'
    )
    list_filter = ('content_type', 'is_free', 'course__category', 'created_at')
    search_fields = ('title', 'content', 'course__title')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'slug')
        }),
        ('Content', {
            'fields': (
                'content_type', 'content', 'video_url', 'code_example'
            )
        }),
        ('Learning Information', {
            'fields': ('learning_objectives', 'key_concepts')
        }),
        ('Settings', {
            'fields': ('estimated_reading_time', 'order', 'is_free')
        }),
    )
    
    def content_type_badge(self, obj):
        colors = {
            'text': 'blue',
            'video': 'green',
            'interactive': 'purple',
            'code': 'orange'
        }
        color = colors.get(obj.content_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_content_type_display()
        )
    content_type_badge.short_description = 'Type'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin for Course Enrollments"""
    
    list_display = (
        'user', 'course', 'status_badge', 'progress_bar',
        'enrolled_at', 'last_accessed'
    )
    list_filter = (
        'status', 'course__category', 'course__level', 
        'enrolled_at', 'completed_at'
    )
    search_fields = (
        'user__username', 'user__email', 'course__title'
    )
    readonly_fields = (
        'progress_percentage', 'enrolled_at', 'completed_at', 'last_accessed'
    )
    
    fieldsets = (
        ('Enrollment Details', {
            'fields': ('user', 'course', 'status')
        }),
        ('Progress', {
            'fields': ('progress_percentage', 'completed_lessons')
        }),
        ('Timestamps', {
            'fields': ('enrolled_at', 'completed_at', 'last_accessed'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('completed_lessons',)
    
    def status_badge(self, obj):
        colors = {
            'active': 'blue',
            'completed': 'green',
            'paused': 'orange',
            'dropped': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progress_bar(self, obj):
        percentage = obj.progress_percentage
        color = 'green' if percentage == 100 else 'blue' if percentage > 50 else 'orange'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px; overflow: hidden;">' +
            '<div style="width: {}%; height: 20px; background-color: {}; text-align: center; color: white; font-size: 11px; line-height: 20px;">' +
            '{}%</div></div>',
            percentage, color, int(percentage)
        )
    progress_bar.short_description = 'Progress'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'course'
        ).prefetch_related('completed_lessons')

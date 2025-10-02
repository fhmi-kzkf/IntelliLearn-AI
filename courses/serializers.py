from rest_framework import serializers
from .models import Category, Course, Lesson, Enrollment
from accounts.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'order', 'course_count']
    
    def get_course_count(self, obj):
        return obj.courses.filter(status='published').count()


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'content_type', 'content', 'video_url', 'code_example',
            'learning_objectives', 'key_concepts', 'estimated_reading_time', 'order',
            'is_free', 'created_at', 'updated_at'
        ]


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    lessons_count = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description', 'category', 'category_name',
            'level', 'level_display', 'thumbnail', 'estimated_duration', 'instructor', 'instructor_name',
            'status', 'points_reward', 'order', 'view_count', 'enrollment_count', 'created_at',
            'updated_at', 'published_at', 'lessons_count'
        ]
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(CourseSerializer):
    """Serializer for detailed Course view with lessons"""
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['lessons']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_thumbnail = serializers.ImageField(source='course.thumbnail', read_only=True)
    instructor_name = serializers.CharField(source='course.instructor.get_full_name', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'course', 'course_title', 'course_thumbnail', 'instructor_name',
            'status', 'progress_percentage', 'enrolled_at', 'completed_at', 'last_accessed'
        ]
        read_only_fields = ['user', 'enrolled_at', 'completed_at', 'last_accessed']


class CourseProgressSerializer(serializers.ModelSerializer):
    """Serializer for course progress tracking"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    total_lessons = serializers.SerializerMethodField()
    completed_lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'status', 'progress_percentage', 
            'total_lessons', 'completed_lessons_count', 'enrolled_at', 'completed_at'
        ]
    
    def get_total_lessons(self, obj):
        return obj.course.lessons.count()
    
    def get_completed_lessons_count(self, obj):
        return obj.completed_lessons.count()
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    """Categories for organizing AI courses"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    color = models.CharField(max_length=7, default='#E02424', help_text="Hex color code")
    
    # Ordering and visibility
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'course_categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']


class Course(models.Model):
    """AI learning courses with micro-learning approach"""
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Course organization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='unlocks')
    
    # Content
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    estimated_duration = models.PositiveIntegerField(
        help_text="Estimated duration in minutes",
        validators=[MinValueValidator(5), MaxValueValidator(120)]
    )
    
    # Instructor and status
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_courses',
        limit_choices_to={'role__in': ['mentor', 'admin']}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Gamification
    points_reward = models.PositiveIntegerField(default=50)
    
    # Ordering and metrics
    order = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    enrollment_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_level_color(self):
        """Return color class for course level"""
        colors = {
            'beginner': 'bg-green-100 text-green-800',
            'intermediate': 'bg-yellow-100 text-yellow-800',
            'advanced': 'bg-red-100 text-red-800',
        }
        return colors.get(self.level, 'bg-gray-100 text-gray-800')
    
    def is_published(self):
        return self.status == 'published'
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['order', '-created_at']


class Lesson(models.Model):
    """Individual lessons within a course (micro-learning units)"""
    
    CONTENT_TYPE_CHOICES = [
        ('text', 'Text Content'),
        ('video', 'Video'),
        ('interactive', 'Interactive Content'),
        ('code', 'Code Example'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    
    # Content
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text')
    content = models.TextField(help_text="Main lesson content")
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    code_example = models.TextField(blank=True, help_text="Code snippets or examples")
    
    # Learning objectives
    learning_objectives = models.TextField(blank=True, help_text="What learners will achieve")
    key_concepts = models.TextField(blank=True, help_text="Key concepts covered")
    
    # Lesson settings
    estimated_reading_time = models.PositiveIntegerField(
        default=5,
        help_text="Estimated reading/completion time in minutes"
    )
    order = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    class Meta:
        db_table = 'lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['order']
        unique_together = ['course', 'slug']


class Enrollment(models.Model):
    """Track user enrollment in courses"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('dropped', 'Dropped'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Progress tracking
    progress_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    completed_lessons = models.ManyToManyField(Lesson, blank=True, related_name='completed_by')
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    def update_progress(self):
        """Calculate and update progress percentage"""
        total_lessons = self.course.lessons.count()
        if total_lessons > 0:
            completed_count = self.completed_lessons.count()
            self.progress_percentage = (completed_count / total_lessons) * 100
            
            # Mark as completed if all lessons are done
            if self.progress_percentage == 100.0 and self.status == 'active':
                self.status = 'completed'
                self.completed_at = timezone.now()
            
            self.save()
    
    class Meta:
        db_table = 'course_enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']

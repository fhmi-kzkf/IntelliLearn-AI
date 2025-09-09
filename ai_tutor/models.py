from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class AITutorSession(models.Model):
    """AI tutor chat sessions"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('paused', 'Paused'),
    ]
    
    CONTEXT_CHOICES = [
        ('general', 'General AI Questions'),
        ('course', 'Course-specific Help'),
        ('quiz', 'Quiz Assistance'),
        ('concept', 'Concept Explanation'),
        ('troubleshooting', 'Problem Solving'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    
    # Session context
    context_type = models.CharField(max_length=20, choices=CONTEXT_CHOICES, default='general')
    context_object_type = models.CharField(max_length=50, blank=True, help_text="Type of related object (course, quiz, etc.)")
    context_object_id = models.PositiveIntegerField(blank=True, null=True, help_text="ID of related object")
    
    # Session details
    title = models.CharField(max_length=200, blank=True, help_text="Auto-generated or user-set title")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Metadata
    total_messages = models.PositiveIntegerField(default=0)
    user_satisfaction = models.PositiveIntegerField(
        blank=True, null=True,
        choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
        help_text="User rating for the session"
    )
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title or f'Session {self.session_id[:8]}'}"
    
    def end_session(self):
        """End the AI tutor session"""
        self.status = 'ended'
        self.ended_at = timezone.now()
        self.save()
    
    def get_duration(self):
        """Get session duration"""
        if self.ended_at:
            return self.ended_at - self.started_at
        return timezone.now() - self.started_at
    
    class Meta:
        db_table = 'ai_tutor_sessions'
        verbose_name = 'AI Tutor Session'
        verbose_name_plural = 'AI Tutor Sessions'
        ordering = ['-last_activity']


class AITutorMessage(models.Model):
    """Individual messages in AI tutor conversations"""
    
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Tutor'),
        ('system', 'System'),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('code', 'Code Example'),
        ('explanation', 'Concept Explanation'),
        ('suggestion', 'Learning Suggestion'),
        ('feedback', 'Feedback'),
        ('quiz_hint', 'Quiz Hint'),
    ]
    
    session = models.ForeignKey(AITutorSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    
    # Message content
    content = models.TextField()
    formatted_content = models.TextField(blank=True, help_text="HTML formatted content")
    
    # AI metadata
    ai_model = models.CharField(max_length=50, blank=True, help_text="AI model used for response")
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    
    # Message evaluation
    was_helpful = models.BooleanField(blank=True, null=True, help_text="User feedback on AI response")
    user_feedback = models.TextField(blank=True, help_text="Additional user feedback")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.get_sender_display()}: {content_preview}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update session message count and last activity
        self.session.total_messages = self.session.messages.count()
        self.session.last_activity = timezone.now()
        self.session.save()
    
    class Meta:
        db_table = 'ai_tutor_messages'
        verbose_name = 'AI Tutor Message'
        verbose_name_plural = 'AI Tutor Messages'
        ordering = ['created_at']


class AIGeneratedContent(models.Model):
    """Track AI-generated content for courses, quizzes, etc."""
    
    CONTENT_TYPE_CHOICES = [
        ('quiz_question', 'Quiz Question'),
        ('course_material', 'Course Material'),
        ('explanation', 'Concept Explanation'),
        ('example', 'Code Example'),
        ('exercise', 'Practice Exercise'),
        ('feedback', 'Personalized Feedback'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]
    
    # Content identification
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Generation details
    prompt = models.TextField(help_text="Prompt used to generate this content")
    ai_model = models.CharField(max_length=50, help_text="AI model used")
    generation_parameters = models.JSONField(default=dict, help_text="Parameters used for generation")
    
    # Content metadata
    target_level = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        blank=True
    )
    topic_tags = models.JSONField(default=list, help_text="List of topic tags")
    
    # Review and approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_content',
        help_text="User who triggered the generation"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_content',
        help_text="User who reviewed the content"
    )
    
    # Quality metrics
    quality_score = models.FloatField(blank=True, null=True, help_text="Auto-generated quality score (0-1)")
    human_rating = models.PositiveIntegerField(
        blank=True, null=True,
        choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]
    )
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_content_type_display()}: {self.title}"
    
    def approve_content(self, reviewer):
        """Approve the generated content"""
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.save()
    
    def publish_content(self):
        """Publish the approved content"""
        if self.status == 'approved':
            self.status = 'published'
            self.save()
    
    def increment_usage(self):
        """Track content usage"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save()
    
    class Meta:
        db_table = 'ai_generated_content'
        verbose_name = 'AI Generated Content'
        verbose_name_plural = 'AI Generated Content'
        ordering = ['-created_at']


class PersonalizedRecommendation(models.Model):
    """AI-generated personalized learning recommendations"""
    
    RECOMMENDATION_TYPE_CHOICES = [
        ('course', 'Course Recommendation'),
        ('topic', 'Topic to Study'),
        ('review', 'Content to Review'),
        ('practice', 'Practice Exercise'),
        ('path', 'Learning Path'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('accepted', 'Accepted'),
        ('dismissed', 'Dismissed'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)
    
    # Recommendation content
    title = models.CharField(max_length=200)
    description = models.TextField()
    reason = models.TextField(help_text="Why this is recommended")
    
    # Target content
    target_object_type = models.CharField(max_length=50, blank=True)
    target_object_id = models.PositiveIntegerField(blank=True, null=True)
    
    # AI generation details
    confidence_score = models.FloatField(help_text="AI confidence in this recommendation (0-1)")
    based_on_data = models.JSONField(default=dict, help_text="Data used to generate recommendation")
    
    # User interaction
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    viewed_at = models.DateTimeField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    # Priority and expiration
    priority = models.PositiveIntegerField(default=5, help_text="1 (highest) to 10 (lowest)")
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_viewed(self):
        """Mark recommendation as viewed"""
        if self.status == 'pending':
            self.status = 'viewed'
            self.viewed_at = timezone.now()
            self.save()
    
    def accept_recommendation(self):
        """User accepts the recommendation"""
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
    
    def dismiss_recommendation(self):
        """User dismisses the recommendation"""
        self.status = 'dismissed'
        self.responded_at = timezone.now()
        self.save()
    
    def is_expired(self):
        """Check if recommendation has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    class Meta:
        db_table = 'personalized_recommendations'
        verbose_name = 'Personalized Recommendation'
        verbose_name_plural = 'Personalized Recommendations'
        ordering = ['priority', '-created_at']

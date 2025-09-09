from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Custom User model for IntelliLearn AI platform"""
    
    ROLE_CHOICES = [
        ('learner', 'Learner'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='learner')
    learning_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Gamification fields
    total_points = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(blank=True, null=True)
    
    # Learning preferences
    preferred_learning_time = models.PositiveIntegerField(
        default=15,
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        help_text="Preferred learning session duration in minutes"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_learner(self):
        return self.role == 'learner'
    
    def is_mentor(self):
        return self.role == 'mentor'
    
    def is_admin_user(self):
        return self.role == 'admin'
    
    def get_level_display_color(self):
        """Return color class for user level"""
        colors = {
            'beginner': 'text-green-500',
            'intermediate': 'text-yellow-500',
            'advanced': 'text-red-500',
        }
        return colors.get(self.learning_level, 'text-gray-500')
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class UserProfile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Learning goals and preferences
    learning_goals = models.TextField(blank=True, help_text="User's learning objectives")
    interests = models.TextField(blank=True, help_text="AI topics of interest")
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    weekly_digest = models.BooleanField(default=True)
    
    # Social features
    is_public_profile = models.BooleanField(default=False)
    show_progress = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

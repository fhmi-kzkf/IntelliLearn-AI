from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class Quiz(models.Model):
    """Interactive quizzes for AI learning assessment"""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    SOURCE_CHOICES = [
        ('manual', 'Created by Mentor'),
        ('ai_generated', 'AI Generated'),
        ('hybrid', 'AI Assisted'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Quiz organization
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    
    # Quiz settings
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    time_limit = models.PositiveIntegerField(
        default=0,
        help_text="Time limit in minutes (0 = no limit)"
    )
    max_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Maximum attempts allowed (0 = unlimited)"
    )
    
    # Content source
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_quizzes'
    )
    
    # Gamification
    points_per_question = models.PositiveIntegerField(default=10)
    bonus_points = models.PositiveIntegerField(default=0)
    
    # Status and settings
    is_active = models.BooleanField(default=True)
    shuffle_questions = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_total_points(self):
        """Calculate total possible points for this quiz"""
        return self.questions.count() * self.points_per_question + self.bonus_points
    
    def get_difficulty_color(self):
        """Return color class for quiz difficulty"""
        colors = {
            'easy': 'bg-green-100 text-green-800',
            'medium': 'bg-yellow-100 text-yellow-800',
            'hard': 'bg-red-100 text-red-800',
        }
        return colors.get(self.difficulty, 'bg-gray-100 text-gray-800')
    
    class Meta:
        db_table = 'quizzes'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']


class Question(models.Model):
    """Individual questions within quizzes"""
    
    TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('fill_blank', 'Fill in the Blank'),
        ('short_answer', 'Short Answer'),
        ('code_completion', 'Code Completion'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice')
    
    # Question content
    text = models.TextField(help_text="The question text")
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    code_snippet = models.TextField(blank=True, help_text="Code example or snippet")
    
    # Question settings
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=10)
    
    # AI generation metadata
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True, help_text="Prompt used for AI generation")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"
    
    def get_correct_answer(self):
        """Get the correct answer for this question"""
        return self.choices.filter(is_correct=True).first()
    
    def get_correct_answers(self):
        """Get all correct answers (for multiple correct answers)"""
        return self.choices.filter(is_correct=True)
    
    class Meta:
        db_table = 'quiz_questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['order']


class Choice(models.Model):
    """Answer choices for multiple choice questions"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField(help_text="Choice text")
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # Optional explanation for this choice
    explanation = models.TextField(blank=True, help_text="Why this choice is correct/incorrect")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.question.quiz.title} - {self.text[:50]}"
    
    class Meta:
        db_table = 'quiz_choices'
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'
        ordering = ['order']


class QuizAttempt(models.Model):
    """Track user attempts at quizzes"""
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('time_expired', 'Time Expired'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    # Attempt details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.PositiveIntegerField(default=0)
    percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_taken = models.DurationField(blank=True, null=True)
    
    # Attempt number for this user-quiz combination
    attempt_number = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} (Attempt {self.attempt_number})"
    
    def calculate_score(self):
        """Calculate the total score for this attempt"""
        total_score = 0
        for answer in self.answers.all():
            if answer.is_correct:
                total_score += answer.question.points
        
        self.score = total_score
        
        # Calculate percentage
        total_possible = self.quiz.get_total_points()
        if total_possible > 0:
            self.percentage = (total_score / total_possible) * 100
        
        self.save()
        return total_score
    
    def complete_attempt(self):
        """Mark attempt as completed and calculate final score"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.time_taken = self.completed_at - self.started_at
        self.calculate_score()
    
    class Meta:
        db_table = 'quiz_attempts'
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
        ordering = ['-started_at']
        unique_together = ['user', 'quiz', 'attempt_number']


class Answer(models.Model):
    """User answers to quiz questions"""
    
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    
    # Answer content (flexible for different question types)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, blank=True, null=True)
    text_answer = models.TextField(blank=True, help_text="For text-based answers")
    
    # Answer evaluation
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveIntegerField(default=0)
    
    # AI evaluation for subjective answers
    ai_evaluated = models.BooleanField(default=False)
    ai_feedback = models.TextField(blank=True, help_text="AI-generated feedback")
    
    # Timestamps
    answered_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.text[:50]}"
    
    def evaluate_answer(self):
        """Evaluate if the answer is correct"""
        if self.question.question_type == 'multiple_choice':
            if self.selected_choice and self.selected_choice.is_correct:
                self.is_correct = True
                self.points_earned = self.question.points
        elif self.question.question_type == 'true_false':
            if self.selected_choice and self.selected_choice.is_correct:
                self.is_correct = True
                self.points_earned = self.question.points
        # For other types, manual or AI evaluation might be needed
        
        self.save()
    
    class Meta:
        db_table = 'quiz_answers'
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        unique_together = ['attempt', 'question']

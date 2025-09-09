from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from courses.models import Course, Category
from quizzes.models import Quiz, QuizAttempt
from gamification.models import Badge, UserBadge
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class AdminDashboardView(UserPassesTestMixin, TemplateView):
    """Admin dashboard with system statistics"""
    template_name = 'admin_dashboard.html'
    
    def test_func(self):
        """Only allow admin users"""
        return self.request.user.is_authenticated and (
            self.request.user.is_superuser or 
            self.request.user.role == 'admin'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User statistics
        total_users = User.objects.count()
        admin_users = User.objects.filter(Q(is_superuser=True) | Q(role='admin')).count()
        mentor_users = User.objects.filter(role='mentor').count()
        learner_users = User.objects.filter(role='learner').count()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_registrations = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        
        # Course statistics
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(status='published').count()
        draft_courses = Course.objects.filter(status='draft').count()
        total_categories = Category.objects.count()
        
        # Quiz statistics
        total_quizzes = Quiz.objects.count()
        total_quiz_attempts = QuizAttempt.objects.count()
        completed_attempts = QuizAttempt.objects.filter(status='completed').count()
        avg_quiz_score = QuizAttempt.objects.filter(status='completed').aggregate(
            avg_score=Avg('percentage')
        )['avg_score'] or 0
        
        # Badge statistics
        total_badges = Badge.objects.count()
        awarded_badges = UserBadge.objects.count()
        
        # Learning level distribution
        level_distribution = User.objects.values('learning_level').annotate(
            count=Count('id')
        ).order_by('learning_level')
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_quiz_attempts = QuizAttempt.objects.filter(
            started_at__gte=week_ago
        ).count()
        recent_badge_awards = UserBadge.objects.filter(
            earned_at__gte=week_ago
        ).count()
        
        # Top performers
        top_learners = User.objects.filter(role='learner').order_by('-total_points')[:5]
        
        context.update({
            # User stats
            'total_users': total_users,
            'admin_users': admin_users,
            'mentor_users': mentor_users,
            'learner_users': learner_users,
            'recent_registrations': recent_registrations,
            
            # Course stats
            'total_courses': total_courses,
            'published_courses': published_courses,
            'draft_courses': draft_courses,
            'total_categories': total_categories,
            
            # Quiz stats
            'total_quizzes': total_quizzes,
            'total_quiz_attempts': total_quiz_attempts,
            'completed_attempts': completed_attempts,
            'avg_quiz_score': round(avg_quiz_score, 1),
            
            # Badge stats
            'total_badges': total_badges,
            'awarded_badges': awarded_badges,
            
            # Distributions and trends
            'level_distribution': level_distribution,
            'recent_quiz_attempts': recent_quiz_attempts,
            'recent_badge_awards': recent_badge_awards,
            'top_learners': top_learners,
        })
        
        return context
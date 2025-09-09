from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from quizzes.models import QuizAttempt
from courses.models import Enrollment, Course
from gamification.models import UserBadge, Badge
from django.db.models import Count, Q


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view with user progress data"""
    template_name = 'dashboard.html'
    
    def get(self, request, *args, **kwargs):
        # Redirect to login if not authenticated
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Redirect admins to admin dashboard
        if request.user.is_superuser or request.user.role == 'admin':
            return redirect('admin_dashboard')
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Dashboard statistics
        context.update({
            'completed_quizzes_count': QuizAttempt.objects.filter(
                user=user, 
                status='completed'
            ).count(),
            'enrolled_courses_count': Enrollment.objects.filter(user=user).count(),
            'earned_badges_count': UserBadge.objects.filter(user=user).count(),
            'total_points': getattr(user, 'total_points', 0),
            'current_streak': getattr(user, 'current_streak', 0),
        })
        
        # Recent activity
        recent_enrollments = Enrollment.objects.filter(
            user=user
        ).select_related('course').order_by('-enrolled_at')[:3]
        
        recent_quiz_attempts = QuizAttempt.objects.filter(
            user=user,
            status='completed'
        ).select_related('quiz').order_by('-completed_at')[:3]
        
        recent_badges = UserBadge.objects.filter(
            user=user
        ).select_related('badge').order_by('-earned_at')[:3]
        
        # Available courses (not enrolled)
        enrolled_course_ids = Enrollment.objects.filter(
            user=user
        ).values_list('course_id', flat=True)
        
        available_courses = Course.objects.filter(
            status='published'
        ).exclude(
            id__in=enrolled_course_ids
        ).order_by('-created_at')[:3]
        
        context.update({
            'recent_enrollments': recent_enrollments,
            'recent_quiz_attempts': recent_quiz_attempts,
            'recent_badges': recent_badges,
            'available_courses': available_courses,
        })
        
        return context
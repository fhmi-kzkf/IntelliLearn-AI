from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Avg, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Badge, UserBadge, PointTransaction, LearningStreak, Leaderboard
from accounts.models import User


class BadgeListView(ListView):
    """List all available badges with user progress"""
    model = Badge
    template_name = 'gamification/badges.html'
    context_object_name = 'badges'
    
    def get_queryset(self):
        return Badge.objects.filter(is_active=True).order_by('badge_type', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            # Get user's earned badges
            user_badges = UserBadge.objects.filter(
                user=self.request.user
            ).values_list('badge_id', flat=True)
            
            # Add earned status to badges
            for badge in context['badges']:
                badge.is_earned = badge.id in user_badges
                badge.earned_count = badge.user_badges.count()
                
                # Calculate progress for some badges (simplified logic)
                if not badge.is_earned:
                    badge.progress = self.calculate_badge_progress(badge)
        
        return context
    
    def calculate_badge_progress(self, badge):
        """Calculate user progress towards earning a badge"""
        user = self.request.user
        
        if badge.badge_type == 'completion':
            # For course completion badges
            if 'first' in badge.name.lower():
                completed_courses = user.enrollments.filter(status='completed').count()
                return min(completed_courses, badge.requirement_value) / badge.requirement_value * 100
            elif 'explorer' in badge.name.lower():
                completed_courses = user.enrollments.filter(status='completed').count()
                return min(completed_courses, 3) / 3 * 100
        
        elif badge.badge_type == 'quiz':
            if 'perfect' in badge.name.lower():
                best_score = user.quiz_attempts.filter(
                    status='completed'
                ).aggregate(best=models.Max('percentage'))['best'] or 0
                return min(best_score, 100)
        
        elif badge.badge_type == 'streak':
            current_streak = getattr(user, 'current_streak', 0)
            if '7' in badge.requirement_description:
                return min(current_streak, 7) / 7 * 100
            elif '30' in badge.requirement_description:
                return min(current_streak, 30) / 30 * 100
        
        return 0


class BadgeDetailView(TemplateView):
    """Badge detail view with earning requirements and statistics"""
    template_name = 'gamification/badge_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        badge = get_object_or_404(Badge, id=kwargs['badge_id'], is_active=True)
        
        context['badge'] = badge
        context['earned_count'] = badge.user_badges.count()
        context['total_users'] = User.objects.filter(is_active=True).count()
        
        if self.request.user.is_authenticated:
            context['is_earned'] = UserBadge.objects.filter(
                user=self.request.user,
                badge=badge
            ).exists()
        
        return context


class MyBadgesView(LoginRequiredMixin, TemplateView):
    """User's earned badges with achievements timeline"""
    template_name = 'gamification/my_badges.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's badges ordered by most recent
        user_badges = UserBadge.objects.filter(
            user=self.request.user
        ).select_related('badge').order_by('-earned_at')
        
        # Group by badge type
        badges_by_type = {}
        for user_badge in user_badges:
            badge_type = user_badge.badge.get_badge_type_display()
            if badge_type not in badges_by_type:
                badges_by_type[badge_type] = []
            badges_by_type[badge_type].append(user_badge)
        
        context['user_badges'] = user_badges
        context['badges_by_type'] = badges_by_type
        context['total_badges'] = user_badges.count()
        context['total_points_from_badges'] = user_badges.aggregate(
            total=Sum('points_awarded')
        )['total'] or 0
        
        return context


class LeaderboardView(TemplateView):
    """Dynamic leaderboard with multiple metrics and periods"""
    template_name = 'gamification/leaderboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        metric = kwargs.get('metric', 'total_points')
        period = kwargs.get('period', 'all_time')
        
        # Calculate period dates
        now = timezone.now()
        if period == 'daily':
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            period_start = now - timedelta(days=7)
        elif period == 'monthly':
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # all_time
            period_start = None
        
        # Get leaderboard data based on metric
        if metric == 'total_points':
            leaderboard = self.get_points_leaderboard(period_start)
        elif metric == 'courses_completed':
            leaderboard = self.get_courses_leaderboard(period_start)
        elif metric == 'quiz_average':
            leaderboard = self.get_quiz_leaderboard(period_start)
        elif metric == 'current_streak':
            leaderboard = self.get_streak_leaderboard()
        else:
            leaderboard = []
        
        context.update({
            'leaderboard': leaderboard[:50],  # Top 50
            'current_metric': metric,
            'current_period': period,
            'user_rank': self.get_user_rank(leaderboard) if self.request.user.is_authenticated else None,
        })
        
        return context
    
    def get_points_leaderboard(self, period_start=None):
        """Get leaderboard based on total points"""
        queryset = User.objects.filter(is_active=True)
        
        if period_start:
            # Calculate points for specific period
            queryset = queryset.annotate(
                period_points=Sum(
                    'point_transactions__points',
                    filter=Q(point_transactions__created_at__gte=period_start)
                )
            ).filter(period_points__gt=0).order_by('-period_points')
        else:
            queryset = queryset.order_by('-total_points')
        
        return list(queryset[:50])
    
    def get_courses_leaderboard(self, period_start=None):
        """Get leaderboard based on completed courses"""
        queryset = User.objects.filter(is_active=True).annotate(
            completed_courses=Count(
                'enrollments',
                filter=Q(enrollments__status='completed')
            )
        )
        
        if period_start:
            queryset = queryset.annotate(
                period_completions=Count(
                    'enrollments',
                    filter=Q(
                        enrollments__status='completed',
                        enrollments__completed_at__gte=period_start
                    )
                )
            ).filter(period_completions__gt=0).order_by('-period_completions')
        else:
            queryset = queryset.filter(completed_courses__gt=0).order_by('-completed_courses')
        
        return list(queryset[:50])
    
    def get_quiz_leaderboard(self, period_start=None):
        """Get leaderboard based on quiz average scores"""
        queryset = User.objects.filter(is_active=True).annotate(
            quiz_average=Avg(
                'quiz_attempts__percentage',
                filter=Q(quiz_attempts__status='completed')
            )
        )
        
        if period_start:
            queryset = queryset.annotate(
                period_average=Avg(
                    'quiz_attempts__percentage',
                    filter=Q(
                        quiz_attempts__status='completed',
                        quiz_attempts__completed_at__gte=period_start
                    )
                )
            ).filter(period_average__isnull=False).order_by('-period_average')
        else:
            queryset = queryset.filter(quiz_average__isnull=False).order_by('-quiz_average')
        
        return list(queryset[:50])
    
    def get_streak_leaderboard(self):
        """Get leaderboard based on current learning streaks"""
        return list(
            User.objects.filter(
                is_active=True,
                current_streak__gt=0
            ).order_by('-current_streak')[:50]
        )
    
    def get_user_rank(self, leaderboard):
        """Get current user's rank in the leaderboard"""
        for idx, user in enumerate(leaderboard):
            if user.id == self.request.user.id:
                return idx + 1
        return None


class PointsView(LoginRequiredMixin, TemplateView):
    """User's points overview with earning history"""
    template_name = 'gamification/points.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent point transactions
        recent_transactions = PointTransaction.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:20]
        
        # Calculate points by source
        points_by_source = PointTransaction.objects.filter(
            user=self.request.user,
            transaction_type='earned'
        ).values('source').annotate(
            total_points=Sum('points')
        ).order_by('-total_points')
        
        context.update({
            'recent_transactions': recent_transactions,
            'points_by_source': points_by_source,
            'total_earned': self.request.user.total_points,
        })
        
        return context


class PointsHistoryView(LoginRequiredMixin, ListView):
    """Complete points transaction history"""
    template_name = 'gamification/points_history.html'
    context_object_name = 'transactions'
    paginate_by = 50
    
    def get_queryset(self):
        return PointTransaction.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class StreakView(LoginRequiredMixin, TemplateView):
    """Learning streak information and management"""
    template_name = 'gamification/streak.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create learning streak
        streak, created = LearningStreak.objects.get_or_create(
            user=self.request.user
        )
        
        # Check if streak needs to be updated
        streak.check_streak_broken()
        
        context['streak'] = streak
        return context


class UpdateStreakView(LoginRequiredMixin, TemplateView):
    """Update learning streak (called when user completes activities)"""
    
    def post(self, request, *args, **kwargs):
        streak, created = LearningStreak.objects.get_or_create(
            user=request.user
        )
        
        new_streak = streak.update_streak()
        
        # Award streak bonus points
        if new_streak > 0 and new_streak % 7 == 0:  # Weekly milestone
            bonus_points = int(new_streak * 10)  # 10 points per day in streak
            
            PointTransaction.objects.create(
                user=request.user,
                transaction_type='bonus',
                source='streak_bonus',
                points=bonus_points,
                description=f'Weekly streak bonus: {new_streak} days',
                balance_after=request.user.total_points + bonus_points
            )
            
            request.user.total_points += bonus_points
            request.user.save()
            
            messages.success(request, f'Streak milestone reached! +{bonus_points} bonus points!')
        
        return JsonResponse({
            'status': 'success',
            'current_streak': new_streak,
            'longest_streak': streak.longest_streak
        })


class AchievementsView(LoginRequiredMixin, TemplateView):
    """Overview of user achievements and progress"""
    template_name = 'gamification/achievements.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user statistics
        user_stats = {
            'total_badges': UserBadge.objects.filter(user=self.request.user).count(),
            'total_points': self.request.user.total_points,
            'courses_completed': self.request.user.enrollments.filter(status='completed').count(),
            'quizzes_completed': self.request.user.quiz_attempts.filter(status='completed').count(),
            'current_streak': getattr(self.request.user, 'current_streak', 0),
        }
        
        # Get recent achievements
        recent_badges = UserBadge.objects.filter(
            user=self.request.user
        ).select_related('badge').order_by('-earned_at')[:5]
        
        context.update({
            'user_stats': user_stats,
            'recent_badges': recent_badges,
        })
        
        return context


class CheckAchievementsView(LoginRequiredMixin, TemplateView):
    """Check for new achievements and award them"""
    
    def post(self, request, *args, **kwargs):
        new_badges = self.check_and_award_badges(request.user)
        
        if new_badges:
            messages.success(
                request, 
                f'Congratulations! You earned {len(new_badges)} new badge(s)!'
            )
            return JsonResponse({
                'status': 'success',
                'new_badges': [badge.name for badge in new_badges]
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': 'No new achievements found. Keep learning!'
            })
    
    def check_and_award_badges(self, user):
        """Check if user qualifies for any new badges"""
        new_badges = []
        
        # Get all badges user hasn't earned yet
        earned_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        available_badges = Badge.objects.filter(
            is_active=True
        ).exclude(id__in=earned_badge_ids)
        
        for badge in available_badges:
            if self.check_badge_requirement(user, badge):
                # Award the badge
                UserBadge.objects.create(
                    user=user,
                    badge=badge,
                    points_awarded=badge.points_value
                )
                
                # Add points to user
                user.total_points += badge.points_value
                
                # Create point transaction
                PointTransaction.objects.create(
                    user=user,
                    transaction_type='earned',
                    source='badge_earned',
                    points=badge.points_value,
                    description=f'Badge earned: {badge.name}',
                    balance_after=user.total_points,
                    context_object_type='badge',
                    context_object_id=badge.id
                )
                
                new_badges.append(badge)
        
        if new_badges:
            user.save()
        
        return new_badges
    
    def check_badge_requirement(self, user, badge):
        """Check if user meets badge requirements (simplified logic)"""
        if badge.badge_type == 'completion':
            completed_courses = user.enrollments.filter(status='completed').count()
            return completed_courses >= badge.requirement_value
        
        elif badge.badge_type == 'quiz':
            if 'master' in badge.name.lower():
                high_scores = user.quiz_attempts.filter(
                    status='completed',
                    percentage__gte=90
                ).count()
                return high_scores >= badge.requirement_value
        
        elif badge.badge_type == 'streak':
            current_streak = getattr(user, 'current_streak', 0)
            return current_streak >= badge.requirement_value
        
        return False

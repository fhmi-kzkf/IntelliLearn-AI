from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import Quiz, Question, Choice, QuizAttempt, Answer
from courses.models import Course, Category
import json


class QuizListView(ListView):
    """List all available quizzes with filtering and search"""
    model = Quiz
    template_name = 'quizzes/list.html'
    context_object_name = 'quizzes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Quiz.objects.filter(is_active=True).select_related(
            'created_by', 'course'
        ).prefetch_related('questions')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(course__category__slug=category)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add quiz statistics
        for quiz in context['quizzes']:
            quiz.question_count = quiz.questions.count()
            quiz.attempt_count = quiz.attempts.count()
            quiz.average_score = quiz.attempts.filter(
                status='completed'
            ).aggregate(avg_score=Avg('percentage'))['avg_score'] or 0
            
        # Add categories for the filter section
        categories = Category.objects.filter(is_active=True).order_by('order')
        # Annotate each category with quiz count
        categories = categories.annotate(quiz_count=Count('courses__quizzes', filter=Q(courses__quizzes__is_active=True)))
        
        context['categories'] = categories
        
        return context


class QuizDetailView(DetailView):
    """Quiz detail view with information before starting"""
    model = Quiz
    template_name = 'quizzes/detail.html'
    context_object_name = 'quiz'
    pk_url_kwarg = 'quiz_id'
    
    def get_object(self):
        quiz = get_object_or_404(Quiz, id=self.kwargs['quiz_id'], is_active=True)
        return quiz
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = context['quiz']
        
        # Add quiz statistics
        context['question_count'] = quiz.questions.count()
        context['attempt_count'] = quiz.attempts.count()
        context['average_score'] = quiz.attempts.filter(
            status='completed'
        ).aggregate(avg_score=Avg('percentage'))['avg_score'] or 0
        
        # Calculate pass grade (70% of total points)
        total_points = quiz.get_total_points()
        pass_grade_points = total_points * 0.7
        context['pass_grade_points'] = round(pass_grade_points)
        
        # Check if user has previous attempts
        if self.request.user.is_authenticated:
            context['user_attempts'] = quiz.attempts.filter(
                user=self.request.user
            ).order_by('-started_at')[:5]
            
            context['best_score'] = quiz.attempts.filter(
                user=self.request.user,
                status='completed'
            ).aggregate(best=Avg('percentage'))['best'] or 0
        
        return context


class StartQuizView(LoginRequiredMixin, TemplateView):
    """Start a new quiz attempt"""
    
    def post(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=kwargs['quiz_id'], is_active=True)
        
        # Check if user has reached max attempts
        if quiz.max_attempts > 0:
            user_attempts = quiz.attempts.filter(
                user=request.user
            ).count()
            
            if user_attempts >= quiz.max_attempts:
                messages.error(request, f'You have reached the maximum number of attempts ({quiz.max_attempts}) for this quiz.')
                return redirect('quizzes:detail', quiz_id=quiz.id)
        
        # Create new attempt
        attempt_number = quiz.attempts.filter(user=request.user).count() + 1
        
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            attempt_number=attempt_number,
            status='in_progress'
        )
        
        messages.success(request, 'Quiz started! Good luck!')
        return redirect('quizzes:take', quiz_id=quiz.id, attempt_id=attempt.id)
    
    def get(self, request, *args, **kwargs):
        return redirect('quizzes:detail', quiz_id=kwargs['quiz_id'])


class TakeQuizView(LoginRequiredMixin, TemplateView):
    """Take quiz interface"""
    template_name = 'quizzes/take.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get quiz and attempt
        quiz = get_object_or_404(Quiz, id=kwargs['quiz_id'], is_active=True)
        attempt = get_object_or_404(
            QuizAttempt, 
            id=kwargs['attempt_id'], 
            user=self.request.user,
            quiz=quiz
        )
        
        # Check if attempt is still active
        if attempt.status != 'in_progress':
            messages.info(self.request, 'This quiz attempt has already been completed.')
            return redirect('quizzes:results', quiz_id=quiz.id, attempt_id=attempt.id)
        
        # Get questions with shuffle if enabled
        questions = quiz.questions.all().prefetch_related('choices')
        if quiz.shuffle_questions:
            questions = questions.order_by('?')
        else:
            questions = questions.order_by('order')
        
        # Get current question (default to first)
        current_question_index = int(self.request.GET.get('q', 1)) - 1
        if current_question_index >= len(questions):
            current_question_index = 0
        
        current_question = questions[current_question_index]
        
        # Get user's answer for this question if exists
        user_answer = Answer.objects.filter(
            attempt=attempt,
            question=current_question
        ).first()
        
        # Calculate time limit in seconds for the template
        time_limit_seconds = quiz.time_limit * 60 if quiz.time_limit > 0 else 0
        
        context.update({
            'quiz': quiz,
            'attempt': attempt,
            'questions': questions,
            'current_question': current_question,
            'current_question_index': current_question_index,
            'total_questions': len(questions),
            'user_answer': user_answer,
            'progress_percentage': ((current_question_index + 1) / len(questions)) * 100,
            'time_limit_seconds': time_limit_seconds,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        # Get quiz and attempt
        quiz_id = kwargs['quiz_id']
        attempt_id = kwargs['attempt_id']
        
        quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
        attempt = get_object_or_404(
            QuizAttempt, 
            id=attempt_id, 
            user=request.user,
            quiz=quiz
        )
        
        # Check if attempt is still active
        if attempt.status != 'in_progress':
            messages.info(request, 'This quiz attempt has already been completed.')
            return redirect('quizzes:results', quiz_id=quiz.id, attempt_id=attempt.id)
        
        # Get questions with shuffle if enabled
        questions = quiz.questions.all().prefetch_related('choices')
        if quiz.shuffle_questions:
            questions = questions.order_by('?')
        else:
            questions = questions.order_by('order')
        
        # Get current question index
        current_question_index = int(request.GET.get('q', 1)) - 1
        if current_question_index >= len(questions):
            current_question_index = 0
        
        current_question = questions[current_question_index]
        
        # Process answer
        answer_data = request.POST.get(f'question_{current_question.id}')
        if answer_data:
            # Create or update answer
            answer, created = Answer.objects.get_or_create(
                attempt=attempt,
                question=current_question,
                defaults={'text_answer': answer_data}
            )
            
            if not created:
                answer.text_answer = answer_data
            
            # For multiple choice questions
            if current_question.question_type == 'multiple_choice':
                try:
                    choice_id = int(answer_data)
                    choice = Choice.objects.get(id=choice_id, question=current_question)
                    answer.selected_choice = choice
                    # Evaluate the answer immediately
                    answer.evaluate_answer()
                except (ValueError, Choice.DoesNotExist):
                    answer.selected_choice = None
                    answer.is_correct = False
                    answer.points_earned = 0
                    answer.save()
            
            # For true/false questions
            elif current_question.question_type == 'true_false':
                if answer_data in ['True', 'False']:
                    answer.text_answer = answer_data
                    # For true/false, we need to find the correct choice
                    correct_choice = current_question.choices.filter(
                        is_correct=True, 
                        text=answer_data
                    ).first()
                    if correct_choice:
                        answer.selected_choice = correct_choice
                        answer.is_correct = True
                        answer.points_earned = current_question.points
                    else:
                        answer.selected_choice = None
                        answer.is_correct = False
                        answer.points_earned = 0
                    answer.save()
                else:
                    answer.is_correct = False
                    answer.points_earned = 0
                    answer.save()
            
            # For other question types, save without evaluation
            else:
                answer.save()
        
        # Determine next question index
        next_question_index = current_question_index + 1
        if next_question_index >= len(questions):
            next_question_index = current_question_index  # Stay on current question if at the end
        
        # Redirect to the next question or stay on current
        next_url = f"{request.path}?q={next_question_index + 1}"
        return redirect(next_url)


class SubmitQuizView(LoginRequiredMixin, TemplateView):
    """Submit quiz and calculate results"""
    
    def post(self, request, *args, **kwargs):
        try:
            quiz = get_object_or_404(Quiz, id=kwargs['quiz_id'], is_active=True)
            attempt = get_object_or_404(
                QuizAttempt, 
                id=kwargs['attempt_id'], 
                user=request.user,
                quiz=quiz
            )
            
            # Check if attempt is still in progress
            if attempt.status != 'in_progress':
                messages.info(request, 'This quiz attempt has already been completed or submitted.')
                return redirect('quizzes:results', quiz_id=quiz.id, attempt_id=attempt.id)
            
            # Process answers and calculate score
            for question in quiz.questions.all():
                answer_data = request.POST.get(f'question_{question.id}')
                if answer_data:
                    # Create or update answer
                    answer, created = Answer.objects.get_or_create(
                        attempt=attempt,
                        question=question,
                        defaults={'text_answer': answer_data}
                    )
                    
                    if not created:
                        answer.text_answer = answer_data
                    
                    # For multiple choice questions
                    if question.question_type == 'multiple_choice':
                        try:
                            choice_id = int(answer_data)
                            choice = Choice.objects.get(id=choice_id, question=question)
                            answer.selected_choice = choice
                        except (ValueError, Choice.DoesNotExist):
                            pass
                    
                    # Evaluate answer
                    answer.evaluate_answer()
            
            # Complete the attempt
            attempt.complete_attempt()
            
            # Award points to user
            if attempt.status == 'completed':
                points_earned = attempt.score
                request.user.total_points += points_earned
                request.user.save()
                
                # Create point transaction
                from gamification.models import PointTransaction
                PointTransaction.objects.create(
                    user=request.user,
                    transaction_type='earned',
                    source='quiz_completion',
                    points=points_earned,
                    description=f'Completed quiz: {quiz.title}',
                    balance_after=request.user.total_points,
                    context_object_type='quiz',
                    context_object_id=quiz.id
                )
            
            messages.success(request, 'Quiz submitted successfully!')
        except Exception as e:
            messages.error(request, f'Error submitting quiz: {str(e)}')
            return redirect('quizzes:take', quiz_id=quiz.id, attempt_id=attempt.id)
        
        return redirect('quizzes:results', quiz_id=quiz.id, attempt_id=attempt.id)


class QuizResultsView(LoginRequiredMixin, TemplateView):
    """Display quiz results with detailed feedback"""
    template_name = 'quizzes/results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get quiz and attempt
        quiz = get_object_or_404(Quiz, id=kwargs['quiz_id'])
        attempt = get_object_or_404(
            QuizAttempt, 
            id=kwargs['attempt_id'], 
            user=self.request.user,
            quiz=quiz
        )
        
        # Get all answers with questions and choices
        answers = attempt.answers.all().select_related(
            'question', 'selected_choice'
        ).prefetch_related('question__choices')
        
        # Calculate performance by topic (placeholder logic)
        performance_analysis = {
            'strengths': [
                {'topic': 'Supervised Learning', 'score': 90},
                {'topic': 'Algorithm Selection', 'score': 85},
            ],
            'weaknesses': [
                {'topic': 'Feature Engineering', 'score': 60},
                {'topic': 'Model Evaluation', 'score': 45},
            ]
        }
        
        # Get user's rank for this quiz
        better_attempts = QuizAttempt.objects.filter(
            quiz=quiz,
            status='completed',
            percentage__gt=attempt.percentage
        ).count()
        
        user_rank = better_attempts + 1
        total_attempts = quiz.attempts.filter(status='completed').count()
        
        context.update({
            'quiz': quiz,
            'attempt': attempt,
            'answers': answers,
            'performance_analysis': performance_analysis,
            'user_rank': user_rank,
            'total_attempts': total_attempts,
        })
        
        return context


class MyQuizAttemptsView(LoginRequiredMixin, ListView):
    """User's quiz attempt history"""
    template_name = 'quizzes/my_attempts.html'
    context_object_name = 'attempts'
    paginate_by = 20
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(
            user=self.request.user
        ).select_related('quiz').order_by('-started_at')


# Placeholder views for remaining functionality
class QuizSearchView(ListView):
    """Quiz search view"""
    model = Quiz
    template_name = 'quizzes/search.html'
    context_object_name = 'quizzes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Quiz.objects.filter(is_active=True).select_related(
            'created_by', 'course'
        ).prefetch_related('questions')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(course__category__slug=category)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add quiz statistics
        for quiz in context['quizzes']:
            quiz.question_count = quiz.questions.count()
            quiz.attempt_count = quiz.attempts.count()
            quiz.average_score = quiz.attempts.filter(
                status='completed'
            ).aggregate(avg_score=Avg('percentage'))['avg_score'] or 0
            
        # Add categories for the filter section
        categories = Category.objects.filter(is_active=True).order_by('order')
        # Annotate each category with quiz count
        categories = categories.annotate(quiz_count=Count('courses__quizzes', filter=Q(courses__quizzes__is_active=True)))
        
        context['categories'] = categories
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_difficulty'] = self.request.GET.get('difficulty', '')
        context['selected_category'] = self.request.GET.get('category', '')
        
        return context


class CreateQuizView(LoginRequiredMixin, TemplateView):
    """Create new quiz (mentors only)"""
    template_name = 'quizzes/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_mentor or request.user.is_admin_user):
            messages.error(request, 'You need mentor privileges to create quizzes.')
            return redirect('quizzes:list')
        return super().dispatch(request, *args, **kwargs)


class EditQuizView(LoginRequiredMixin, TemplateView):
    """Edit quiz (mentors only)"""
    template_name = 'quizzes/edit.html'


class AddQuestionView(LoginRequiredMixin, TemplateView):
    """Add question to quiz"""
    template_name = 'quizzes/add_question.html'


class EditQuestionView(LoginRequiredMixin, TemplateView):
    """Edit question"""
    template_name = 'quizzes/edit_question.html'


class GenerateQuestionsView(LoginRequiredMixin, TemplateView):
    """AI-generated questions"""
    template_name = 'quizzes/generate_questions.html'


class AIQuizSuggestionsView(LoginRequiredMixin, TemplateView):
    """AI quiz suggestions"""
    template_name = 'quizzes/ai_suggestions.html'

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Quiz, Question, Choice, QuizAttempt, Answer
from .serializers import (
    QuizSerializer, QuizDetailSerializer, QuestionSerializer, ChoiceSerializer,
    QuizAttemptSerializer, QuizAttemptCreateSerializer, AnswerSubmitSerializer
)
from courses.models import Course


class QuizListView(generics.ListAPIView):
    """API view for listing quizzes"""
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Quiz.objects.filter(is_active=True).select_related('course', 'created_by')


class QuizDetailView(generics.RetrieveAPIView):
    """API view for quiz detail"""
    queryset = Quiz.objects.filter(is_active=True).select_related('course', 'created_by')
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_quiz_attempt(request, quiz_id):
    """API endpoint for starting a quiz attempt"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user has attempts left
    if quiz.max_attempts > 0:
        user_attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
        if user_attempts >= quiz.max_attempts:
            return Response({
                'error': 'Maximum attempts reached for this quiz'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        attempt_number=QuizAttempt.objects.filter(user=request.user, quiz=quiz).count() + 1
    )
    
    serializer = QuizAttemptSerializer(attempt)
    return Response({
        'attempt': serializer.data,
        'message': 'Quiz attempt started successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_answer(request, attempt_id):
    """API endpoint for submitting a quiz answer"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, status='in_progress')
    
    serializer = AnswerSubmitSerializer(data=request.data)
    if serializer.is_valid():
        # Check if answer already exists for this question
        question = serializer.validated_data['question']
        existing_answer = Answer.objects.filter(attempt=attempt, question=question).first()
        
        if existing_answer:
            # Update existing answer
            existing_answer.selected_choice = serializer.validated_data['selected_choice']
            existing_answer.is_correct = existing_answer.selected_choice.is_correct
            existing_answer.save()
        else:
            # Create new answer
            answer = serializer.save(attempt=attempt)
            answer.is_correct = answer.selected_choice.is_correct
            answer.save()
        
        return Response({
            'message': 'Answer submitted successfully'
        }, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_quiz_attempt(request, attempt_id):
    """API endpoint for completing a quiz attempt"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, status='in_progress')
    
    # Calculate score
    attempt.calculate_score()
    attempt.status = 'completed'
    attempt.save()
    
    serializer = QuizAttemptSerializer(attempt)
    return Response({
        'attempt': serializer.data,
        'message': 'Quiz completed successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_quiz_attempts(request):
    """API endpoint for user's quiz attempts"""
    attempts = QuizAttempt.objects.filter(user=request.user).select_related(
        'quiz__course'
    ).prefetch_related('answers__question', 'answers__selected_choice').order_by('-started_at')
    
    serializer = QuizAttemptSerializer(attempts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def quiz_attempt_detail(request, attempt_id):
    """API endpoint for quiz attempt detail"""
    attempt = get_object_or_404(
        QuizAttempt, 
        id=attempt_id, 
        user=request.user
    ).select_related('quiz__course').prefetch_related('answers__question', 'answers__selected_choice')
    
    serializer = QuizAttemptSerializer(attempt)
    return Response(serializer.data)
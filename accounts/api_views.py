from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in
from .models import User
from .serializers import UserSerializer, UserProfileSerializer, UserRegistrationSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """API view for user detail and profile updates"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """API view for updating user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """API endpoint for user login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            # Send signal for login
            user_logged_in.send(sender=User, request=request, user=user)
            
            # Return user data and token
            user_serializer = UserSerializer(user)
            return Response({
                'user': user_serializer.data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({
            'error': 'Username and password required'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def user_logout(request):
    """API endpoint for user logout"""
    try:
        # Delete the token to logout
        request.user.auth_token.delete()
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'error': 'Error logging out'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_register(request):
    """API endpoint for user registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)
        # Serialize user data
        user_serializer = UserSerializer(user)
        return Response({
            'user': user_serializer.data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_data(request):
    """API endpoint for user dashboard data"""
    user = request.user
    user_serializer = UserSerializer(user)
    
    # Get recent enrollments
    from courses.models import Enrollment
    from courses.serializers import CourseProgressSerializer
    recent_enrollments = Enrollment.objects.filter(user=user).select_related('course').order_by('-enrolled_at')[:5]
    enrollments_serializer = CourseProgressSerializer(recent_enrollments, many=True)
    
    # Get recent quiz attempts
    from quizzes.models import QuizAttempt
    from quizzes.serializers import QuizAttemptSerializer
    recent_attempts = QuizAttempt.objects.filter(user=user).select_related('quiz').order_by('-started_at')[:5]
    attempts_serializer = QuizAttemptSerializer(recent_attempts, many=True)
    
    # Get recent badges
    from gamification.models import UserBadge
    from gamification.serializers import UserBadgeSerializer
    recent_badges = UserBadge.objects.filter(user=user).select_related('badge').order_by('-earned_at')[:5]
    badges_serializer = UserBadgeSerializer(recent_badges, many=True)
    
    return Response({
        'user': user_serializer.data,
        'recent_enrollments': enrollments_serializer.data,
        'recent_quiz_attempts': attempts_serializer.data,
        'recent_badges': badges_serializer.data,
        'stats': {
            'enrolled_courses': recent_enrollments.count(),
            'completed_quizzes': recent_attempts.filter(status='completed').count(),
            'earned_badges': recent_badges.count(),
            'total_points': user.total_points,
            'current_streak': user.current_streak
        }
    })
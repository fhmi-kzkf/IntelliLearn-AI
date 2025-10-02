from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Category, Course, Lesson, Enrollment
from .serializers import (
    CategorySerializer, CourseSerializer, CourseDetailSerializer, 
    LessonSerializer, EnrollmentSerializer, CourseProgressSerializer
)
from accounts.models import User


class CategoryListView(generics.ListAPIView):
    """API view for listing categories"""
    queryset = Category.objects.all().order_by('order', 'name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CourseListView(generics.ListAPIView):
    """API view for listing courses"""
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'category__name']
    ordering_fields = ['title', 'created_at', 'enrollment_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Course.objects.filter(status='published').select_related('category', 'instructor')


class CourseDetailView(generics.RetrieveAPIView):
    """API view for course detail"""
    queryset = Course.objects.filter(status='published').select_related('category', 'instructor')
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'


class LessonDetailView(generics.RetrieveAPIView):
    """API view for lesson detail"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_in_course(request, course_id):
    """API endpoint for enrolling in a course"""
    course = get_object_or_404(Course, id=course_id, status='published')
    user = request.user
    
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=user,
        course=course,
        defaults={'status': 'active'}
    )
    
    serializer = EnrollmentSerializer(enrollment)
    if created:
        return Response({
            'enrollment': serializer.data,
            'message': 'Successfully enrolled in course'
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'enrollment': serializer.data,
            'message': 'Already enrolled in this course'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_enrollments(request):
    """API endpoint for user's enrollments"""
    enrollments = Enrollment.objects.filter(user=request.user).select_related(
        'course__category', 'course__instructor'
    ).order_by('-enrolled_at')
    
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course_progress(request, course_id):
    """API endpoint for course progress"""
    enrollment = get_object_or_404(
        Enrollment, 
        user=request.user, 
        course_id=course_id
    )
    
    serializer = CourseProgressSerializer(enrollment)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_lesson_complete(request, course_id, lesson_id):
    """API endpoint for marking a lesson as complete"""
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course_id=course_id
    )
    
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
    
    # Add lesson to completed lessons
    enrollment.completed_lessons.add(lesson)
    
    # Update progress
    enrollment.update_progress()
    
    serializer = CourseProgressSerializer(enrollment)
    return Response({
        'progress': serializer.data,
        'message': 'Lesson marked as complete'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_courses(request):
    """API endpoint for courses not yet enrolled in"""
    # Get IDs of courses user is already enrolled in
    enrolled_course_ids = Enrollment.objects.filter(
        user=request.user
    ).values_list('course_id', flat=True)
    
    # Get available courses
    available_courses = Course.objects.filter(
        status='published'
    ).exclude(
        id__in=enrolled_course_ids
    ).select_related('category', 'instructor').order_by('-created_at')
    
    serializer = CourseSerializer(available_courses, many=True)
    return Response(serializer.data)
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .models import Category, Course, Lesson, Enrollment


class CourseListView(ListView):
    """List all available courses"""
    template_name = 'courses/list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(status='published').select_related('category', 'instructor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        return context


class CategoryView(TemplateView):
    """Course category view"""
    template_name = 'courses/category.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)
        context['category'] = category
        context['courses'] = Course.objects.filter(category=category, status='published').select_related('category', 'instructor')
        return context


class CourseSearchView(TemplateView):
    """Course search view"""
    template_name = 'courses/search.html'


class CourseDetailView(TemplateView):
    """Course detail view"""
    template_name = 'courses/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=slug, status='published')
        context['course'] = course
        context['lessons'] = course.lessons.all()
        
        # Check if user is enrolled
        if self.request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(user=self.request.user, course=course)
                context['enrollment'] = enrollment
                context['is_enrolled'] = True
            except Enrollment.DoesNotExist:
                context['is_enrolled'] = False
        else:
            context['is_enrolled'] = False
            
        return context


class EnrollView(LoginRequiredMixin, TemplateView):
    """Course enrollment view"""
    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=slug, status='published')
        
        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': 'active'}
        )
        
        if created:
            # Increment enrollment count
            course.enrollment_count += 1
            course.save()
            messages.success(request, f'Successfully enrolled in {course.title}!')
        else:
            messages.info(request, f'You are already enrolled in {course.title}.')
            
        return redirect('courses:detail', slug=slug)


class UnenrollView(LoginRequiredMixin, TemplateView):
    """Course unenrollment view"""
    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=slug)
        
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            enrollment.delete()
            
            # Decrement enrollment count
            if course.enrollment_count > 0:
                course.enrollment_count -= 1
                course.save()
                
            messages.success(request, f'Successfully unenrolled from {course.title}.')
        except Enrollment.DoesNotExist:
            messages.error(request, 'You are not enrolled in this course.')
            
        return redirect('courses:detail', slug=slug)


class CourseLearningView(LoginRequiredMixin, TemplateView):
    """Course learning interface"""
    template_name = 'courses/learn.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_slug = self.kwargs.get('course_slug')
        course = get_object_or_404(Course, slug=course_slug, status='published')
        
        # Check if user is enrolled
        try:
            enrollment = Enrollment.objects.get(user=self.request.user, course=course)
        except Enrollment.DoesNotExist:
            messages.error(self.request, 'You must be enrolled in this course to access it.')
            return redirect('courses:detail', slug=course_slug)
        
        context['course'] = course
        context['enrollment'] = enrollment
        context['lessons'] = course.lessons.all()
        
        # Get first lesson if none specified
        lesson_slug = self.kwargs.get('lesson_slug')
        if lesson_slug:
            context['current_lesson'] = get_object_or_404(Lesson, course=course, slug=lesson_slug)
        elif course.lessons.exists():
            context['current_lesson'] = course.lessons.first()
            
        return context


class LessonView(LoginRequiredMixin, TemplateView):
    """Individual lesson view"""
    template_name = 'courses/lesson.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_slug = self.kwargs.get('course_slug')
        lesson_slug = self.kwargs.get('lesson_slug')
        
        course = get_object_or_404(Course, slug=course_slug, status='published')
        lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
        
        # Check if user is enrolled
        try:
            enrollment = Enrollment.objects.get(user=self.request.user, course=course)
        except Enrollment.DoesNotExist:
            messages.error(self.request, 'You must be enrolled in this course to access lessons.')
            return redirect('courses:detail', slug=course_slug)
        
        context['course'] = course
        context['lesson'] = lesson
        context['enrollment'] = enrollment
        context['lessons'] = course.lessons.all()
        
        return context


class CompleteLessonView(LoginRequiredMixin, TemplateView):
    """Mark lesson as complete"""
    def post(self, request, *args, **kwargs):
        course_slug = self.kwargs.get('course_slug')
        lesson_slug = self.kwargs.get('lesson_slug')
        
        course = get_object_or_404(Course, slug=course_slug, status='published')
        lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
        
        # Check if user is enrolled
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
        except Enrollment.DoesNotExist:
            messages.error(request, 'You must be enrolled in this course to complete lessons.')
            return redirect('courses:detail', slug=course_slug)
        
        # Mark lesson as completed
        enrollment.completed_lessons.add(lesson)
        enrollment.update_progress()
        
        messages.success(request, f'Lesson "{lesson.title}" marked as complete!')
        return redirect('courses:lesson', course_slug=course_slug, lesson_slug=lesson_slug)


class CourseProgressView(LoginRequiredMixin, TemplateView):
    """Course progress view"""
    template_name = 'courses/progress.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=slug, status='published')
        
        # Check if user is enrolled
        try:
            enrollment = Enrollment.objects.get(user=self.request.user, course=course)
        except Enrollment.DoesNotExist:
            messages.error(self.request, 'You must be enrolled in this course to view progress.')
            return redirect('courses:detail', slug=slug)
        
        context['course'] = course
        context['enrollment'] = enrollment
        context['completed_lessons'] = enrollment.completed_lessons.all()
        return context


class MyCoursesView(LoginRequiredMixin, TemplateView):
    """User's enrolled courses"""
    template_name = 'courses/my_courses.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrollments'] = Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course__category', 'course__instructor')
        return context


class CreateCourseView(LoginRequiredMixin, TemplateView):
    """Create new course (mentors only)"""
    template_name = 'courses/create.html'


class EditCourseView(LoginRequiredMixin, TemplateView):
    """Edit course (mentors only)"""
    template_name = 'courses/edit.html'


class AddLessonView(LoginRequiredMixin, TemplateView):
    """Add lesson to course"""
    template_name = 'courses/add_lesson.html'


class EditLessonView(LoginRequiredMixin, TemplateView):
    """Edit lesson"""
    template_name = 'courses/edit_lesson.html'
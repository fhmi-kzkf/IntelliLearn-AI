from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class CourseListView(ListView):
    """List all available courses"""
    template_name = 'courses/list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return []


class CategoryView(TemplateView):
    """Course category view"""
    template_name = 'courses/category.html'


class CourseSearchView(TemplateView):
    """Course search view"""
    template_name = 'courses/search.html'


class CourseDetailView(TemplateView):
    """Course detail view"""
    template_name = 'courses/detail.html'


class EnrollView(LoginRequiredMixin, TemplateView):
    """Course enrollment view"""
    def get(self, request, *args, **kwargs):
        messages.info(request, 'Course enrollment feature coming soon!')
        return redirect('courses:list')


class UnenrollView(LoginRequiredMixin, TemplateView):
    """Course unenrollment view"""
    def get(self, request, *args, **kwargs):
        messages.info(request, 'Course unenrollment feature coming soon!')
        return redirect('courses:list')


class CourseLearningView(LoginRequiredMixin, TemplateView):
    """Course learning interface"""
    template_name = 'courses/learn.html'


class LessonView(LoginRequiredMixin, TemplateView):
    """Individual lesson view"""
    template_name = 'courses/lesson.html'


class CompleteLessonView(LoginRequiredMixin, TemplateView):
    """Mark lesson as complete"""
    def get(self, request, *args, **kwargs):
        messages.success(request, 'Lesson marked as complete!')
        return redirect('courses:learn', course_slug=kwargs.get('course_slug'))


class CourseProgressView(LoginRequiredMixin, TemplateView):
    """Course progress view"""
    template_name = 'courses/progress.html'


class MyCoursesView(LoginRequiredMixin, TemplateView):
    """User's enrolled courses"""
    template_name = 'courses/my_courses.html'


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

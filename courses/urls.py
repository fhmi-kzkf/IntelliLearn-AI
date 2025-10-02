from django.urls import path
from . import views
from . import api_views

app_name = 'courses'

urlpatterns = [
    # Course listing and browsing
    path('', views.CourseListView.as_view(), name='list'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('search/', views.CourseSearchView.as_view(), name='search'),
    
    # User's enrolled courses
    path('my-courses/', views.MyCoursesView.as_view(), name='my_courses'),
    
    # Course details and enrollment
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    path('<slug:slug>/enroll/', views.EnrollView.as_view(), name='enroll'),
    path('<slug:slug>/unenroll/', views.UnenrollView.as_view(), name='unenroll'),
    
    # Learning interface
    path('<slug:course_slug>/learn/', views.CourseLearningView.as_view(), name='learn'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/', views.LessonView.as_view(), name='lesson'),
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/complete/', views.CompleteLessonView.as_view(), name='complete_lesson'),
    
    # Progress tracking
    path('<slug:slug>/progress/', views.CourseProgressView.as_view(), name='progress'),
    
    # Course management (for mentors)
    path('create/', views.CreateCourseView.as_view(), name='create'),
    path('<slug:slug>/edit/', views.EditCourseView.as_view(), name='edit'),
    path('<slug:slug>/lessons/add/', views.AddLessonView.as_view(), name='add_lesson'),
    path('<slug:course_slug>/lessons/<slug:lesson_slug>/edit/', views.EditLessonView.as_view(), name='edit_lesson'),
    
    # API endpoints
    path('api/categories/', api_views.CategoryListView.as_view(), name='api_categories'),
    path('api/courses/', api_views.CourseListView.as_view(), name='api_courses'),
    path('api/courses/<slug:slug>/', api_views.CourseDetailView.as_view(), name='api_course_detail'),
    path('api/courses/<slug:course_slug>/lessons/<slug:lesson_slug>/', api_views.LessonDetailView.as_view(), name='api_lesson_detail'),
    path('api/courses/<int:course_id>/enroll/', api_views.enroll_in_course, name='api_enroll'),
    path('api/my-enrollments/', api_views.my_enrollments, name='api_my_enrollments'),
    path('api/courses/<int:course_id>/progress/', api_views.course_progress, name='api_course_progress'),
    path('api/courses/<int:course_id>/lessons/<int:lesson_id>/complete/', api_views.mark_lesson_complete, name='api_complete_lesson'),
    path('api/available-courses/', api_views.available_courses, name='api_available_courses'),
]
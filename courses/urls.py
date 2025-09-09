from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course listing and browsing
    path('', views.CourseListView.as_view(), name='list'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('search/', views.CourseSearchView.as_view(), name='search'),
    
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
    path('my-courses/', views.MyCoursesView.as_view(), name='my_courses'),
    
    # Course management (for mentors)
    path('create/', views.CreateCourseView.as_view(), name='create'),
    path('<slug:slug>/edit/', views.EditCourseView.as_view(), name='edit'),
    path('<slug:slug>/lessons/add/', views.AddLessonView.as_view(), name='add_lesson'),
    path('<slug:course_slug>/lessons/<slug:lesson_slug>/edit/', views.EditLessonView.as_view(), name='edit_lesson'),
]
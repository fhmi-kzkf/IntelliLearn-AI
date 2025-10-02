from django.urls import path
from . import views
from . import api_views

app_name = 'quizzes'

urlpatterns = [
    # Quiz listing and browsing
    path('', views.QuizListView.as_view(), name='list'),
    path('search/', views.QuizSearchView.as_view(), name='search'),
    
    # Quiz taking
    path('<int:quiz_id>/', views.QuizDetailView.as_view(), name='detail'),
    path('<int:quiz_id>/start/', views.StartQuizView.as_view(), name='start'),
    path('<int:quiz_id>/attempt/<int:attempt_id>/', views.TakeQuizView.as_view(), name='take'),
    path('<int:quiz_id>/attempt/<int:attempt_id>/submit/', views.SubmitQuizView.as_view(), name='submit'),
    
    # Quiz results
    path('<int:quiz_id>/attempt/<int:attempt_id>/results/', views.QuizResultsView.as_view(), name='results'),
    path('my-attempts/', views.MyQuizAttemptsView.as_view(), name='my_attempts'),
    
    # Quiz management (for mentors)
    path('create/', views.CreateQuizView.as_view(), name='create'),
    path('<int:quiz_id>/edit/', views.EditQuizView.as_view(), name='edit'),
    path('<int:quiz_id>/questions/add/', views.AddQuestionView.as_view(), name='add_question'),
    path('<int:quiz_id>/questions/<int:question_id>/edit/', views.EditQuestionView.as_view(), name='edit_question'),
    
    # AI-generated content
    path('<int:quiz_id>/generate-questions/', views.GenerateQuestionsView.as_view(), name='generate_questions'),
    path('ai-suggestions/', views.AIQuizSuggestionsView.as_view(), name='ai_suggestions'),
    
    # API endpoints
    path('api/quizzes/', api_views.QuizListView.as_view(), name='api_quiz_list'),
    path('api/quizzes/<int:pk>/', api_views.QuizDetailView.as_view(), name='api_quiz_detail'),
    path('api/quizzes/<int:quiz_id>/start/', api_views.start_quiz_attempt, name='api_start_quiz'),
    path('api/quizzes/<int:quiz_id>/attempt/<int:attempt_id>/submit/', api_views.submit_answer, name='api_submit_quiz'),
    path('api/quizzes/<int:quiz_id>/attempt/<int:attempt_id>/complete/', api_views.complete_quiz_attempt, name='api_complete_quiz'),
    path('api/quizzes/<int:quiz_id>/attempt/<int:attempt_id>/results/', api_views.quiz_attempt_detail, name='api_quiz_results'),
    path('api/my-attempts/', api_views.my_quiz_attempts, name='api_my_quiz_attempts'),
]
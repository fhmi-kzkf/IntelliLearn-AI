from django.urls import path
from . import views

app_name = 'ai_tutor'

urlpatterns = [
    # AI Chat interface
    path('chat/', views.AIChatView.as_view(), name='chat'),
    path('chat/new/', views.NewChatSessionView.as_view(), name='new_chat'),
    path('chat/<str:session_id>/', views.ChatSessionView.as_view(), name='chat_session'),
    path('chat/<str:session_id>/end/', views.EndChatSessionView.as_view(), name='end_chat'),
    
    # Chat messages
    path('api/send-message/', views.SendMessageView.as_view(), name='send_message'),
    path('api/get-messages/<str:session_id>/', views.GetMessagesView.as_view(), name='get_messages'),
    
    # AI-generated content
    path('generate/content/', views.GenerateContentView.as_view(), name='generate_content'),
    path('generate/quiz-questions/', views.GenerateQuizQuestionsView.as_view(), name='generate_quiz_questions'),
    path('generate/explanations/', views.GenerateExplanationsView.as_view(), name='generate_explanations'),
    
    # Personalized recommendations
    path('recommendations/', views.RecommendationsView.as_view(), name='recommendations'),
    path('recommendations/<int:rec_id>/accept/', views.AcceptRecommendationView.as_view(), name='accept_recommendation'),
    path('recommendations/<int:rec_id>/dismiss/', views.DismissRecommendationView.as_view(), name='dismiss_recommendation'),
    
    # AI content management
    path('content/', views.AIContentListView.as_view(), name='content_list'),
    path('content/<int:content_id>/', views.AIContentDetailView.as_view(), name='content_detail'),
    path('content/<int:content_id>/approve/', views.ApproveContentView.as_view(), name='approve_content'),
    path('content/<int:content_id>/publish/', views.PublishContentView.as_view(), name='publish_content'),
    
    # Session management
    path('sessions/', views.ChatSessionListView.as_view(), name='session_list'),
    path('sessions/<str:session_id>/rate/', views.RateSessionView.as_view(), name='rate_session'),
]
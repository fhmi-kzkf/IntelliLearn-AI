from django.urls import path, include
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
    
    # User profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    
    # Password management
    path('password/change/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Account verification
    path('verify-email/<uidb64>/<token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
    
    # API endpoints
    path('api/user/', api_views.UserDetailView.as_view(), name='api_user_detail'),
    path('api/user/update/', api_views.UserProfileUpdateView.as_view(), name='api_user_update'),
    path('api/login/', api_views.user_login, name='api_login'),
    path('api/logout/', api_views.user_logout, name='api_logout'),
    path('api/register/', api_views.user_register, name='api_register'),
    path('api/dashboard/', api_views.user_dashboard_data, name='api_dashboard'),
]
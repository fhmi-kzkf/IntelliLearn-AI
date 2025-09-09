from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    PasswordResetView as BasePasswordResetView,
    PasswordResetConfirmView as BasePasswordResetConfirmView,
    PasswordChangeView as BasePasswordChangeView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User


class LoginView(BaseLoginView):
    """Custom login view"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


class RegisterView(FormView):
    """User registration view"""
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard')
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        learning_level = request.POST.get('learning_level', 'beginner')
        learning_goal = request.POST.get('learning_goal')
        interests = request.POST.getlist('interests')
        
        # Basic validation
        if not all([first_name, last_name, email, username, password1, password2]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, self.template_name)
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, self.template_name)
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, self.template_name)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, self.template_name)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, self.template_name)
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                learning_level=learning_level,
                role='learner'
            )
            
            # Store additional preferences (in a real app, you'd have separate models for these)
            # For now, we'll just log the user in and show a success message
            
            # Log the user in
            login(request, user)
            
            messages.success(request, f'Welcome to IntelliLearn AI, {first_name}! Your account has been created successfully.')
            
            # Redirect to onboarding or dashboard
            return redirect('accounts:onboarding')
            
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, self.template_name)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'


class EditProfileView(LoginRequiredMixin, TemplateView):
    """Edit user profile view"""
    template_name = 'accounts/edit_profile.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    """User settings view"""
    template_name = 'accounts/settings.html'


class ChangePasswordView(LoginRequiredMixin, BasePasswordChangeView):
    """Change password view"""
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')


class PasswordResetView(BasePasswordResetView):
    """Password reset view"""
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:login')


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    """Password reset confirm view"""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:login')


class VerifyEmailView(TemplateView):
    """Email verification view"""
    template_name = 'accounts/verify_email.html'


class OnboardingView(LoginRequiredMixin, TemplateView):
    """Onboarding view for new users"""
    template_name = 'accounts/onboarding.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Welcome to IntelliLearn AI'
        return context


class ResendVerificationView(LoginRequiredMixin, TemplateView):
    """Resend email verification view"""
    template_name = 'accounts/resend_verification.html'

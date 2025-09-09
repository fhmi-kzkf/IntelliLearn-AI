"""
URL configuration for intellilearn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts.dashboard_views import DashboardView
from accounts.admin_views import AdminDashboardView

# Customize Django Admin
admin.site.site_header = "IntelliLearn AI Admin"
admin.site.site_title = "IntelliLearn AI"
admin.site.index_title = "Welcome to IntelliLearn AI Administration"

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('gamification/', include('gamification.urls')),
    path('ai-tutor/', include('ai_tutor.urls')),
    
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

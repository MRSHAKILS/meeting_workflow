"""
URL configuration for meeting_agent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from landing_page.views import landing_page  # Your landing page view

urlpatterns = [
    path('admin/', admin.site.urls),
    # Allauth’s built-in routes
    path('accounts/', include('allauth.urls')),
    # Your custom login/signup app under /login/
    path('login/', include('login_signup_app.urls')),
    # Meetings dashboard (requires login)
    path('dashboard/', include('create_meeting_app.urls')),
    # Public landing page at root
    path('', landing_page, name='landing_page'),
]


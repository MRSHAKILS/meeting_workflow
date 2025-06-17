from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_meeting, name='create_meeting'),
    path('join/', views.join_meeting, name='join_meeting'),
    path('meeting/<int:meeting_id>/', views.meeting_page, name='meeting_page'),
    path('delete_meeting/<int:meeting_id>/', views.delete_meeting, name='delete_meeting'),
]
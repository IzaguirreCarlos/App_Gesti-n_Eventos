from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('events/<slug:slug>/attendees/', views.event_attendees, name='attendees'),
    path('events/<slug:slug>/export/', views.export_attendees_csv, name='export_csv'),
]

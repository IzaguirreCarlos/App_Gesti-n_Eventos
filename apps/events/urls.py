from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='list'),
    path('events/create/', views.event_create, name='create'),
    path('events/calendar/', views.calendar_view, name='calendar'),
    path('events/calendar/data/', views.calendar_events_api, name='calendar_data'),
    path('events/<slug:slug>/', views.event_detail, name='detail'),
    path('events/<slug:slug>/edit/', views.event_edit, name='edit'),
    path('events/<slug:slug>/delete/', views.event_delete, name='delete'),
]

from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    path('my/', views.my_registrations, name='my_registrations'),
    path('<uuid:pk>/', views.registration_detail, name='detail'),
    path('event/<slug:slug>/register/', views.register_to_event, name='register'),
    path('<uuid:pk>/cancel/', views.cancel_registration, name='cancel'),
]

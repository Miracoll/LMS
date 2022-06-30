from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='front'),
    path('student/result/<str:pk>/', views.result, name='result'),
]
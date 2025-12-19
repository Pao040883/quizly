"""
URL configuration for quizzes app.
"""
from django.urls import path
from .views import (
    create_quiz_view,
    quiz_list_view,
    quiz_detail_view
)

urlpatterns = [
    path('createQuiz/', create_quiz_view, name='create_quiz'),
    path('quizzes/', quiz_list_view, name='quiz_list'),
    path('quizzes/<int:pk>/', quiz_detail_view, name='quiz_detail'),
]

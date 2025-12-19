"""
Models for the quizzes app.
"""
from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    """
    Quiz model to store quiz information.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Question model to store quiz questions.
    """
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_title = models.TextField()
    question_options = models.JSONField()
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['id']

    def __str__(self):
        return f"{self.quiz.title} - Question {self.id}"

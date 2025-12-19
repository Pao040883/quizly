"""
Serializers for quizzes app.
"""
from rest_framework import serializers
from ..models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model.
    """
    class Meta:
        model = Question
        fields = (
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for Quiz model with nested questions.
    """
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = (
            'id',
            'title',
            'description',
            'video_url',
            'questions',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class CreateQuizSerializer(serializers.Serializer):
    """
    Serializer for creating a new quiz from YouTube URL.
    """
    url = serializers.URLField(required=True)

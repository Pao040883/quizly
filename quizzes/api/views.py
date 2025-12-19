"""
Views for quizzes app.
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import Quiz
from .serializers import QuizSerializer, CreateQuizSerializer
from ..functions import create_quiz_from_url
from ..utils import create_question_in_db


def create_quiz_in_db(user, quiz_data, url):
    """
    Create quiz and questions in database.

    Args:
        user: User model instance
        quiz_data: Dictionary with title, description, questions
        url: YouTube video URL string

    Returns:
        Quiz: Created quiz model instance
    """
    quiz = Quiz.objects.create(
        user=user,
        title=quiz_data['title'],
        description=quiz_data.get('description', ''),
        video_url=url
    )
    for q_data in quiz_data['questions']:
        create_question_in_db(quiz, q_data)
    return quiz


def process_quiz_creation(serializer, user):
    """
    Process quiz creation from request data.

    Args:
        serializer: Validated CreateQuizSerializer instance
        user: Authenticated user object

    Returns:
        Response: Created quiz data with 201 status
    """
    url = serializer.validated_data['url']
    quiz_data = create_quiz_from_url(url, user)
    quiz = create_quiz_in_db(user, quiz_data, url)
    return Response(
        QuizSerializer(quiz).data,
        status.HTTP_201_CREATED
    )


class CreateQuizView(APIView):
    """Create quiz from YouTube URL."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create quiz from YouTube URL.

        Args:
            request: HTTP request with YouTube URL

        Returns:
            Response: Created quiz data or error message
        """
        serializer = CreateQuizSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        try:
            return process_quiz_creation(serializer, request.user)
        except Exception as e:
            return Response(
                {'detail': f'Error creating quiz: {str(e)}'},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuizListView(generics.ListAPIView):
    """Get all quizzes for the authenticated user."""
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get all quizzes for the authenticated user.

        Returns:
            QuerySet: User's quizzes
        """
        return Quiz.objects.filter(user=self.request.user)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific quiz."""
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get queryset filtered by authenticated user.

        Returns:
            QuerySet: User's quizzes
        """
        return Quiz.objects.filter(user=self.request.user)

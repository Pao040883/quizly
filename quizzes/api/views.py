"""
Views for quizzes app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import Quiz
from .serializers import QuizSerializer, CreateQuizSerializer
from ..functions import create_quiz_from_url
from ..utils import create_question_in_db


def create_quiz_in_db(user, quiz_data, url):
    """Create quiz and questions in database."""
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
    """Process quiz creation from request data."""
    url = serializer.validated_data['url']
    quiz_data = create_quiz_from_url(url, user)
    quiz = create_quiz_in_db(user, quiz_data, url)
    return Response(
        QuizSerializer(quiz).data,
        status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz_view(request):
    """Create quiz from YouTube URL."""
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_list_view(request):
    """
    Get all quizzes for the authenticated user.
    """
    quizzes = Quiz.objects.filter(user=request.user)
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def handle_get_quiz(quiz):
    """Handle GET request for quiz detail."""
    serializer = QuizSerializer(quiz)
    return Response(serializer.data, status=status.HTTP_200_OK)


def handle_patch_quiz(quiz, data):
    """Handle PATCH request for quiz update."""
    serializer = QuizSerializer(quiz, data=data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


def handle_delete_quiz(quiz):
    """Handle DELETE request for quiz."""
    quiz.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def quiz_detail_view(request, pk):
    """Retrieve, update, or delete a specific quiz."""
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)

    if request.method == 'GET':
        return handle_get_quiz(quiz)
    elif request.method == 'PATCH':
        return handle_patch_quiz(quiz, request.data)
    elif request.method == 'DELETE':
        return handle_delete_quiz(quiz)

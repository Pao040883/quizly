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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz_view(request):
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_list_view(request):
    """
    Get all quizzes for the authenticated user.

    Args:
        request: HTTP request from authenticated user

    Returns:
        Response: List of user's quizzes
    """
    quizzes = Quiz.objects.filter(user=request.user)
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def handle_get_quiz(quiz):
    """
    Handle GET request for quiz detail.

    Args:
        quiz: Quiz model instance

    Returns:
        Response: Serialized quiz data
    """
    serializer = QuizSerializer(quiz)
    return Response(serializer.data, status=status.HTTP_200_OK)


def handle_patch_quiz(quiz, data):
    """
    Handle PATCH request for quiz update.

    Args:
        quiz: Quiz model instance
        data: Dictionary with update fields

    Returns:
        Response: Updated quiz data or validation errors
    """
    serializer = QuizSerializer(quiz, data=data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


def handle_delete_quiz(quiz):
    """
    Handle DELETE request for quiz.

    Args:
        quiz: Quiz model instance

    Returns:
        Response: 204 No Content
    """
    quiz.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def quiz_detail_view(request, pk):
    """
    Retrieve, update, or delete a specific quiz.

    Args:
        request: HTTP request
        pk: Quiz primary key

    Returns:
        Response: Quiz data, updated quiz, or 204 No Content
    """
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)

    if request.method == 'GET':
        return handle_get_quiz(quiz)
    elif request.method == 'PATCH':
        return handle_patch_quiz(quiz, request.data)
    elif request.method == 'DELETE':
        return handle_delete_quiz(quiz)

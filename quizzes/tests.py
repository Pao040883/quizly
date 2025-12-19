"""
Tests for quizzes app.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from .models import Quiz, Question
from .functions import (
    get_youtube_download_opts,
    cleanup_audio_file,
    clean_json_response,
    normalize_question_keys
)


class QuizModelTests(TestCase):
    """Tests for Quiz model."""

    def setUp(self):
        """Set up test user and quiz."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            description='Test Description',
            video_url='https://www.youtube.com/watch?v=test'
        )

    def test_quiz_creation(self):
        """Test quiz is created correctly."""
        self.assertEqual(self.quiz.title, 'Test Quiz')
        self.assertEqual(self.quiz.user, self.user)
        self.assertIsNotNone(self.quiz.created_at)

    def test_quiz_string_representation(self):
        """Test quiz string representation."""
        self.assertEqual(str(self.quiz), 'Test Quiz')


class QuestionModelTests(TestCase):
    """Tests for Question model."""

    def setUp(self):
        """Set up test user, quiz, and question."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            video_url='https://www.youtube.com/watch?v=test'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_title='What is 2+2?',
            question_options=['1', '2', '3', '4'],
            answer='4'
        )

    def test_question_creation(self):
        """Test question is created correctly."""
        self.assertEqual(self.question.question_title, 'What is 2+2?')
        self.assertEqual(self.question.answer, '4')
        self.assertEqual(len(self.question.question_options), 4)

    def test_question_cascade_delete(self):
        """Test question is deleted when quiz is deleted."""
        quiz_id = self.quiz.id
        self.quiz.delete()
        self.assertFalse(Question.objects.filter(quiz_id=quiz_id).exists())


class QuizListViewTests(TestCase):
    """Tests for quiz list endpoint."""

    def setUp(self):
        """Set up test client and authenticated user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(refresh.access_token)
        self.quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            video_url='https://www.youtube.com/watch?v=test'
        )

    def test_get_quizzes_authenticated(self):
        """Test getting quizzes as authenticated user."""
        response = self.client.get('/api/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Quiz')

    def test_get_quizzes_unauthenticated(self):
        """Test getting quizzes without authentication."""
        client = APIClient()
        response = client.get('/api/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_quizzes_only_own(self):
        """Test users only see their own quizzes."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123!'
        )
        Quiz.objects.create(
            user=other_user,
            title='Other Quiz',
            video_url='https://www.youtube.com/watch?v=other'
        )
        response = self.client.get('/api/quizzes/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Quiz')


class QuizDetailViewTests(TestCase):
    """Tests for quiz detail endpoint."""

    def setUp(self):
        """Set up test client and authenticated user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(refresh.access_token)
        self.quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            video_url='https://www.youtube.com/watch?v=test'
        )
        Question.objects.create(
            quiz=self.quiz,
            question_title='Question 1',
            question_options=['A', 'B', 'C', 'D'],
            answer='A'
        )

    def test_get_quiz_detail(self):
        """Test getting quiz detail."""
        response = self.client.get(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Quiz')
        self.assertEqual(len(response.data['questions']), 1)

    def test_patch_quiz(self):
        """Test updating quiz."""
        response = self.client.patch(
            f'/api/quizzes/{self.quiz.id}/',
            {'title': 'Updated Title'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Updated Title')

    def test_delete_quiz(self):
        """Test deleting quiz."""
        quiz_id = self.quiz.id
        response = self.client.delete(f'/api/quizzes/{quiz_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=quiz_id).exists())

    def test_access_other_user_quiz(self):
        """Test accessing another user's quiz."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123!'
        )
        other_quiz = Quiz.objects.create(
            user=other_user,
            title='Other Quiz',
            video_url='https://www.youtube.com/watch?v=other'
        )
        response = self.client.get(f'/api/quizzes/{other_quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UtilityFunctionTests(TestCase):
    """Tests for utility functions."""

    def test_get_youtube_download_opts(self):
        """Test YouTube download options."""
        opts = get_youtube_download_opts('/path/to/output')
        self.assertEqual(opts['format'], 'bestaudio/best')
        self.assertEqual(opts['outtmpl'], '/path/to/output')
        self.assertTrue(opts['quiet'])

    def test_clean_json_response(self):
        """Test JSON response cleaning."""
        text = '```json\n{"key": "value"}\n```'
        cleaned = clean_json_response(text)
        self.assertEqual(cleaned, '{"key": "value"}')

    def test_clean_json_response_no_markers(self):
        """Test cleaning JSON without markers."""
        text = '{"key": "value"}'
        cleaned = clean_json_response(text)
        self.assertEqual(cleaned, '{"key": "value"}')

    def test_normalize_question_keys(self):
        """Test question key normalization."""
        data = {
            'questions': [
                {
                    'question_title': 'Q1',
                    'question_options': ['A', 'B', 'C', 'D']
                }
            ]
        }
        normalized = normalize_question_keys(data)
        self.assertIn('question', normalized['questions'][0])
        self.assertIn('options', normalized['questions'][0])
        self.assertNotIn('question_title', normalized['questions'][0])

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_audio_file(self, mock_remove, mock_exists):
        """Test audio file cleanup."""
        mock_exists.return_value = True
        cleanup_audio_file('/path/to/file.mp3')
        mock_remove.assert_called_once_with('/path/to/file.mp3')

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_audio_file_not_exists(self, mock_remove, mock_exists):
        """Test cleanup when file doesn't exist."""
        mock_exists.return_value = False
        cleanup_audio_file('/path/to/file.mp3')
        mock_remove.assert_not_called()


class FunctionIntegrationTests(TestCase):
    """Integration tests for quiz generation functions."""

    @patch('quizzes.functions.yt_dlp.YoutubeDL')
    def test_download_youtube_audio(self, mock_ytdl):
        """Test YouTube audio download."""
        from quizzes.functions import download_youtube_audio
        mock_instance = mock_ytdl.return_value.__enter__.return_value
        mock_instance.extract_info.return_value = {'id': 'test123'}
        mock_instance.prepare_filename.return_value = '/path/to/test123.mp3'

        result = download_youtube_audio('https://youtube.com/watch?v=test')
        self.assertEqual(result, '/path/to/test123.mp3')
        mock_instance.extract_info.assert_called_once()

    @patch('quizzes.functions.WHISPER_MODEL')
    @patch('quizzes.functions.cleanup_audio_file')
    def test_transcribe_audio(self, mock_cleanup, mock_model):
        """Test audio transcription."""
        from quizzes.functions import transcribe_audio
        mock_model.transcribe.return_value = {'text': 'Test transcript'}

        result = transcribe_audio('/path/to/audio.mp3')
        self.assertEqual(result, 'Test transcript')
        mock_cleanup.assert_called_once_with('/path/to/audio.mp3')

    @patch('quizzes.functions.WHISPER_MODEL')
    @patch('quizzes.functions.cleanup_audio_file')
    def test_transcribe_audio_cleanup_on_error(self, mock_cleanup, mock_model):
        """Test cleanup happens even on transcription error."""
        from quizzes.functions import transcribe_audio
        mock_model.transcribe.side_effect = Exception('Transcription failed')

        with self.assertRaises(Exception):
            transcribe_audio('/path/to/audio.mp3')
        mock_cleanup.assert_called_once_with('/path/to/audio.mp3')

    def test_build_gemini_prompt(self):
        """Test Gemini prompt building."""
        from quizzes.functions import build_gemini_prompt
        prompt = build_gemini_prompt('Test transcript')
        self.assertIn('Test transcript', prompt)
        self.assertIn('JSON format', prompt)
        self.assertIn('10 questions', prompt)

    @patch('quizzes.functions.genai.Client')
    def test_call_gemini_api(self, mock_client):
        """Test Gemini API call."""
        from quizzes.functions import call_gemini_api
        mock_instance = mock_client.return_value
        mock_response = mock_instance.models.generate_content.return_value
        mock_response.text = 'Generated quiz'

        result = call_gemini_api('Test prompt')
        self.assertEqual(result, 'Generated quiz')

    @patch('quizzes.functions.call_gemini_api')
    def test_generate_quiz_with_gemini(self, mock_api):
        """Test complete quiz generation."""
        from quizzes.functions import generate_quiz_with_gemini
        mock_api.return_value = '''{"title": "Test", "questions": [
            {"question_title": "Q1", "question_options": ["A"], "answer": "A"}
        ]}'''

        result = generate_quiz_with_gemini('Test transcript')
        self.assertEqual(result['title'], 'Test')
        self.assertIn('questions', result)

    def test_generate_quiz_no_api_key(self):
        """Test error when API key is missing."""
        from quizzes.functions import generate_quiz_with_gemini
        from django.conf import settings
        original_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = ''

        with self.assertRaises(ValueError):
            generate_quiz_with_gemini('Test')

        settings.GEMINI_API_KEY = original_key

    @patch('quizzes.functions.generate_quiz_with_gemini')
    @patch('quizzes.functions.transcribe_audio')
    @patch('quizzes.functions.download_youtube_audio')
    def test_create_quiz_from_url_integration(
        self, mock_download, mock_transcribe, mock_generate
    ):
        """Test complete quiz creation pipeline."""
        from quizzes.functions import create_quiz_from_url
        mock_download.return_value = '/path/audio.mp3'
        mock_transcribe.return_value = 'Transcript text'
        mock_generate.return_value = {
            'title': 'Quiz',
            'questions': []
        }

        user = User.objects.create_user('testuser', password='test')
        result = create_quiz_from_url('https://youtube.com/watch?v=test', user)

        self.assertEqual(result['title'], 'Quiz')
        mock_download.assert_called_once()
        mock_transcribe.assert_called_once()
        mock_generate.assert_called_once()


class CreateQuizViewTests(TestCase):
    """Tests for quiz creation endpoint."""

    def setUp(self):
        """Set up test client and authenticated user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(refresh.access_token)

    @patch('quizzes.api.views.create_quiz_from_url')
    def test_create_quiz_success(self, mock_create_quiz):
        """Test successful quiz creation."""
        mock_create_quiz.return_value = {
            'title': 'Test Quiz',
            'description': 'Test Description',
            'questions': [
                {
                    'question': 'Q1',
                    'options': ['A', 'B', 'C', 'D'],
                    'answer': 'A'
                }
            ]
        }
        response = self.client.post(
            '/api/createQuiz/',
            {'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Quiz')
        self.assertTrue(Quiz.objects.filter(title='Test Quiz').exists())

    def test_create_quiz_invalid_url(self):
        """Test quiz creation with invalid URL."""
        response = self.client.post(
            '/api/createQuiz/',
            {'url': 'not-a-url'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_quiz_unauthenticated(self):
        """Test quiz creation without authentication."""
        client = APIClient()
        response = client.post(
            '/api/createQuiz/',
            {'url': 'https://www.youtube.com/watch?v=test'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('quizzes.api.views.create_quiz_from_url')
    def test_create_quiz_error_handling(self, mock_create_quiz):
        """Test quiz creation error handling."""
        mock_create_quiz.side_effect = Exception(
            'API Error'
        )
        response = self.client.post(
            '/api/createQuiz/',
            {'url': 'https://www.youtube.com/watch?v=test'},
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Error creating quiz', response.data['detail'])

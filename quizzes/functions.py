"""
Utility functions for quiz generation.
Contains functions for YouTube download, Whisper transcription, and Gemini AI.
"""
import os
import json
import yt_dlp
import whisper
from django.conf import settings
from google import genai

# Preload Whisper model at module level
WHISPER_MODEL = whisper.load_model("tiny")


def get_youtube_download_opts(output_path):
    """
    Get yt-dlp configuration options.

    Args:
        output_path: File path template for downloaded audio

    Returns:
        dict: yt-dlp configuration dictionary
    """
    return {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'noprogress': True,
        'logger': None,
        'no_color': True,
    }


def download_youtube_audio(url):
    """
    Download audio from YouTube URL.

    Args:
        url: YouTube video URL string

    Returns:
        str: Path to downloaded audio file
    """
    output_dir = settings.MEDIA_ROOT / 'temp_audio'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir / '%(id)s.%(ext)s')

    ydl_opts = get_youtube_download_opts(output_path)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_file = ydl.prepare_filename(info)

    return audio_file


def cleanup_audio_file(audio_file_path):
    """
    Remove audio file after processing.

    Args:
        audio_file_path: Path to audio file to delete
    """
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)


def get_prompt_header():
    """
    Get header section of Gemini prompt.

    Returns:
        str: Prompt header with instructions
    """
    return (
        "Based on the following transcript, generate a quiz in "
        "valid JSON format.\n\nThe quiz must follow this exact "
        "structure:"
    )


def get_quiz_structure_dict():
    """
    Get quiz structure as dictionary.

    Returns:
        dict: Quiz structure with title, description, questions
    """
    return {
        "title": (
            "Create a concise quiz title based on the topic of the "
            "transcript."
        ),
        "description": (
            "Summarize the transcript in no more than 150 characters."
        ),
        "questions": [{
            "question_title": "The question goes here.",
            "question_options": [
                "Option A", "Option B", "Option C", "Option D"
            ],
            "answer": "The correct answer from the above options"
        }]
    }


def get_prompt_structure():
    """
    Get JSON structure section of Gemini prompt.

    Returns:
        str: JSON formatted quiz structure example
    """
    structure = get_quiz_structure_dict()
    return (
        json.dumps(structure, indent=2) +
        "\n    ...\n    (exactly 10 questions)"
    )


def get_prompt_requirements():
    """
    Get requirements section of Gemini prompt.

    Returns:
        str: Quiz generation requirements and constraints
    """
    return """
Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be
  present in 'question_options'.
- The output must be valid JSON and parsable as-is
  (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the
  JSON."""


def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Whisper AI.

    Args:
        audio_file_path: Path to audio file

    Returns:
        str: Transcribed text from audio
    """
    try:
        result = WHISPER_MODEL.transcribe(audio_file_path)
        transcript = result["text"]
        return transcript
    finally:
        cleanup_audio_file(audio_file_path)


def build_gemini_prompt(transcript):
    """
    Build prompt for Gemini AI.

    Args:
        transcript: Transcribed text from audio

    Returns:
        str: Complete prompt for Gemini API
    """
    header = get_prompt_header()
    structure = get_prompt_structure()
    requirements = get_prompt_requirements()
    return (
        f"{header}\n\n{structure}\n{requirements}\n\n"
        f"Transcript:\n{transcript}"
    )


def clean_json_response(response_text):
    """
    Remove markdown code blocks from response.

    Args:
        response_text: Raw response from Gemini API

    Returns:
        str: Cleaned JSON string
    """
    text = response_text.strip()
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()


def normalize_question_keys(quiz_data):
    """
    Map response structure to model structure.

    Args:
        quiz_data: Quiz dictionary from Gemini API

    Returns:
        dict: Normalized quiz data for model
    """
    for question in quiz_data.get('questions', []):
        if 'question_title' in question:
            question['question'] = question.pop('question_title')
        if 'question_options' in question:
            question['options'] = question.pop('question_options')
    return quiz_data


def call_gemini_api(prompt):
    """
    Call Gemini API with prompt.

    Args:
        prompt: Complete prompt string for API

    Returns:
        str: Raw response text from Gemini
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


def generate_quiz_with_gemini(transcript):
    """
    Generate quiz from transcript using Gemini AI.

    Args:
        transcript: Transcribed text from audio

    Returns:
        dict: Quiz data with title, description, questions

    Raises:
        ValueError: If GEMINI_API_KEY is not configured
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")

    prompt = build_gemini_prompt(transcript)
    response_text = call_gemini_api(prompt)
    cleaned_text = clean_json_response(response_text)
    quiz_data = json.loads(cleaned_text)
    quiz_data = normalize_question_keys(quiz_data)

    return quiz_data


def create_quiz_from_url(url, user):
    """
    Create quiz from YouTube URL.

    Args:
        url: YouTube video URL
        user: User model instance (currently unused)

    Returns:
        dict: Generated quiz data ready for database
    """
    audio_file = download_youtube_audio(url)
    transcript = transcribe_audio(audio_file)
    quiz_data = generate_quiz_with_gemini(transcript)
    return quiz_data

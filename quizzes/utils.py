"""
Utility functions for quizzes app.
"""


def create_question_in_db(quiz, q_data):
    """Create a single question for a quiz."""
    from .models import Question
    Question.objects.create(
        quiz=quiz,
        question_title=q_data['question'],
        question_options=q_data['options'],
        answer=q_data['answer']
    )

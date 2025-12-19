"""
Management command to download Whisper model.
Run this before first use: python manage.py download_whisper
"""
from django.core.management.base import BaseCommand
import whisper


class Command(BaseCommand):
    help = 'Download Whisper AI model for transcription'

    def handle(self, *args, **options):
        self.stdout.write('Downloading Whisper base model (~140 MB)...')
        self.stdout.write('This only needs to be done once. Please wait...')

        whisper.load_model("base")

        msg = '✓ Whisper model downloaded successfully!'
        self.stdout.write(self.style.SUCCESS(msg))
        self.stdout.write('The model is now cached and ready for use.')
        self.stdout.write('Note: Optimized for videos under 60 seconds.')

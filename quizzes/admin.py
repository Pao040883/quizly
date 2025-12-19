"""
Admin configuration for quizzes app.
"""
from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    """
    Inline admin for Question model.
    """
    model = Question
    extra = 1
    fields = (
        'question_title',
        'question_options',
        'answer'
    )


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Admin for Quiz model.
    """
    list_display = (
        'id',
        'title',
        'user',
        'created_at',
        'updated_at'
    )
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [QuestionInline]

    fieldsets = (
        ('Quiz Information', {
            'fields': ('user', 'title', 'description', 'video_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin for Question model.
    """
    list_display = (
        'id',
        'quiz',
        'question_title',
        'answer'
    )
    list_filter = ('quiz', 'created_at')
    search_fields = (
        'question_title',
        'answer',
        'quiz__title'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Question Information', {
            'fields': (
                'quiz',
                'question_title',
                'question_options',
                'answer'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

"""Django Admin configuration for flashcards core models.

Provides comprehensive admin interface for debugging and data management
with enhanced list displays, filters, and inline editing capabilities.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import AIGenerationSession
from .models import Flashcard


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    """Admin configuration for Flashcard model with debugging features."""

    list_display = (
        "id",
        "front_preview",
        "back_preview",
        "user_email",
        "creation_method",
        "ai_session_link",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "creation_method",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "front",
        "back",
        "user__email",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "front",
                    "back",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "user",
                    "creation_method",
                    "ai_session",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50

    @admin.display(description="Front")
    def front_preview(self, obj: Flashcard) -> str:
        """Display truncated front text."""
        max_length = 50
        if len(obj.front) > max_length:
            return f"{obj.front[:max_length]}..."
        return obj.front

    @admin.display(description="Back")
    def back_preview(self, obj: Flashcard) -> str:
        """Display truncated back text."""
        max_length = 50
        if len(obj.back) > max_length:
            return f"{obj.back[:max_length]}..."
        return obj.back

    @admin.display(description="User", ordering="user__email")
    def user_email(self, obj: Flashcard) -> str:
        """Display user email."""
        return obj.user.email

    @admin.display(description="AI Session")
    def ai_session_link(self, obj: Flashcard) -> str:
        """Display link to associated AI session if exists."""
        if obj.ai_session:
            url = f"/admin/core/aigenerationsession/{obj.ai_session.id}/change/"
            return format_html('<a href="{}">Session #{}</a>', url, obj.ai_session.id)
        return "-"


@admin.register(AIGenerationSession)
class AIGenerationSessionAdmin(admin.ModelAdmin):
    """Admin configuration for AIGenerationSession with inline generated flashcards."""

    list_display = (
        "id",
        "user_email",
        "input_preview",
        "generated_count",
        "model",
        "error_code",
        "api_response_time_ms",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "user__email",
        "input_text",
        "error_message",
    )
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            "Session Info",
            {
                "fields": (
                    "user",
                    "created_at",
                ),
            },
        ),
        (
            "Input",
            {
                "fields": ("input_text",),
            },
        ),
        (
            "Error Details",
            {
                "fields": (
                    "error_code",
                    "error_message",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Performance",
            {
                "fields": ("api_response_time_ms",),
            },
        ),
        (
            "Generation Results",
            {
                "fields": (
                    "model",
                    "generated_count",
                ),
            },
        ),
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50

    @admin.display(description="User", ordering="user__email")
    def user_email(self, obj: AIGenerationSession) -> str:
        """Display user email."""
        return obj.user.email

    @admin.display(description="Input Text")
    def input_preview(self, obj: AIGenerationSession) -> str:
        """Display truncated input text."""
        max_length = 50
        if len(obj.input_text) > max_length:
            return f"{obj.input_text[:max_length]}..."
        return obj.input_text

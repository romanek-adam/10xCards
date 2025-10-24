"""Tests for core flashcard views."""

import pytest
from django.urls import reverse

from flashcards.core.models import Flashcard
from flashcards.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestFlashcardListView:
    """Tests for FlashcardListView."""

    def test_redirects_unauthenticated_user(self, client):
        """Unauthenticated users should be redirected to login."""
        url = reverse("core:flashcard-list")
        response = client.get(url)

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_displays_user_flashcards(self, client):
        """Authenticated users should see their flashcards."""
        user = UserFactory()
        flashcard = Flashcard.objects.create(
            user=user,
            front="Test Question",
            back="Test Answer",
            creation_method=Flashcard.MANUAL,
        )

        client.force_login(user)
        url = reverse("core:flashcard-list")
        response = client.get(url)

        assert response.status_code == 200
        assert flashcard.front in response.content.decode()

    def test_does_not_display_other_users_flashcards(self, client):
        """Users should not see other users' flashcards."""
        user1 = UserFactory()
        user2 = UserFactory()

        flashcard1 = Flashcard.objects.create(
            user=user1,
            front="User 1 Question",
            back="User 1 Answer",
            creation_method=Flashcard.MANUAL,
        )
        flashcard2 = Flashcard.objects.create(
            user=user2,
            front="User 2 Question",
            back="User 2 Answer",
            creation_method=Flashcard.MANUAL,
        )

        client.force_login(user1)
        url = reverse("core:flashcard-list")
        response = client.get(url)

        content = response.content.decode()
        assert flashcard1.front in content
        assert flashcard2.front not in content

    def test_displays_empty_state_when_no_flashcards(self, client):
        """Users with no flashcards should see empty state."""
        user = UserFactory()

        client.force_login(user)
        url = reverse("core:flashcard-list")
        response = client.get(url)

        assert response.status_code == 200
        assert "You don't have any flashcards yet" in response.content.decode()

    def test_pagination_works(self, client):
        """Pagination should display correct number of flashcards per page."""
        user = UserFactory()

        # Create 30 flashcards
        for i in range(30):
            Flashcard.objects.create(
                user=user,
                front=f"Question {i}",
                back=f"Answer {i}",
                creation_method=Flashcard.MANUAL,
            )

        client.force_login(user)
        url = reverse("core:flashcard-list")
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["is_paginated"] is True
        assert len(response.context["flashcards"]) == 25

    def test_page_size_parameter(self, client):
        """Page size can be customized via query parameter."""
        user = UserFactory()

        # Create 60 flashcards
        for i in range(60):
            Flashcard.objects.create(
                user=user,
                front=f"Question {i}",
                back=f"Answer {i}",
                creation_method=Flashcard.MANUAL,
            )

        client.force_login(user)
        url = reverse("core:flashcard-list")
        response = client.get(url, {"page_size": "50"})

        assert response.status_code == 200
        assert len(response.context["flashcards"]) == 50

    def test_page_size_clamped_to_valid_range(self, client):
        """Page size should be clamped to 25-50 range."""
        user = UserFactory()

        # Create 60 flashcards
        for i in range(60):
            Flashcard.objects.create(
                user=user,
                front=f"Question {i}",
                back=f"Answer {i}",
                creation_method=Flashcard.MANUAL,
            )

        client.force_login(user)
        url = reverse("core:flashcard-list")

        # Test upper bound
        response = client.get(url, {"page_size": "100"})
        assert len(response.context["flashcards"]) == 50

        # Test lower bound
        response = client.get(url, {"page_size": "10"})
        assert len(response.context["flashcards"]) == 25

    def test_htmx_request_returns_fragment(self, client):
        """HTMX requests should return fragment template."""
        user = UserFactory()
        Flashcard.objects.create(
            user=user,
            front="Test Question",
            back="Test Answer",
            creation_method=Flashcard.MANUAL,
        )

        client.force_login(user)
        url = reverse("core:flashcard-list")
        response = client.get(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        assert "flashcards/_flashcard_list_items.html" in [
            t.name for t in response.templates
        ]


class TestFlashcardDeleteView:
    """Tests for FlashcardDeleteView."""

    def test_redirects_unauthenticated_user(self, client):
        """Unauthenticated users should be redirected to login."""
        user = UserFactory()
        flashcard = Flashcard.objects.create(
            user=user,
            front="Test Question",
            back="Test Answer",
            creation_method=Flashcard.MANUAL,
        )

        url = reverse("core:flashcard-delete", kwargs={"pk": flashcard.pk})
        response = client.delete(url)

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_deletes_owned_flashcard(self, client):
        """Users should be able to delete their own flashcards."""
        user = UserFactory()
        flashcard = Flashcard.objects.create(
            user=user,
            front="Test Question",
            back="Test Answer",
            creation_method=Flashcard.MANUAL,
        )

        client.force_login(user)
        url = reverse("core:flashcard-delete", kwargs={"pk": flashcard.pk})
        response = client.delete(url)

        assert response.status_code == 200
        assert not Flashcard.objects.filter(pk=flashcard.pk).exists()

    def test_cannot_delete_other_users_flashcard(self, client):
        """Users should not be able to delete other users' flashcards."""
        user1 = UserFactory()
        user2 = UserFactory()

        flashcard = Flashcard.objects.create(
            user=user2,
            front="User 2 Question",
            back="User 2 Answer",
            creation_method=Flashcard.MANUAL,
        )

        client.force_login(user1)
        url = reverse("core:flashcard-delete", kwargs={"pk": flashcard.pk})
        response = client.delete(url)

        assert response.status_code == 404
        assert Flashcard.objects.filter(pk=flashcard.pk).exists()

    def test_returns_updated_list_after_delete(self, client):
        """Delete should return updated flashcard list."""
        user = UserFactory()
        flashcard1 = Flashcard.objects.create(
            user=user,
            front="Question 1",
            back="Answer 1",
            creation_method=Flashcard.MANUAL,
        )
        flashcard2 = Flashcard.objects.create(
            user=user,
            front="Question 2",
            back="Answer 2",
            creation_method=Flashcard.MANUAL,
        )

        client.force_login(user)
        url = reverse("core:flashcard-delete", kwargs={"pk": flashcard1.pk})
        response = client.delete(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert flashcard1.front not in content
        assert flashcard2.front in content

    def test_displays_success_message_after_delete(self, client):
        """Delete should display success message."""
        user = UserFactory()
        flashcard = Flashcard.objects.create(
            user=user,
            front="Test Question",
            back="Test Answer",
            creation_method=Flashcard.MANUAL,
        )

        client.force_login(user)
        url = reverse("core:flashcard-delete", kwargs={"pk": flashcard.pk})
        response = client.delete(url, follow=True)

        messages = list(response.context.get("messages", []))
        assert len(messages) == 1
        assert "successfully" in str(messages[0]).lower()

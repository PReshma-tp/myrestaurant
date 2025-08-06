from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Reshma",
            last_name="TP"
        )
        self.url = reverse('accounts:profile')

    def test_profile_requires_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_profile_loads_for_logged_in_user(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_shows_correct_user_info(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.url)
        self.assertContains(response, "Testuser")
        self.assertContains(response, "test@example.com")

    def test_profile_context_variables_present(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.url)

        expected_context_keys = [
            'bookmarks_count', 'visited_count', 'photos_count', 'reviews_count',
            'bookmarks', 'visited', 'photos', 'reviews'
        ]

        for key in expected_context_keys:
            self.assertIn(key, response.context, msg=f"Missing context key: {key}")

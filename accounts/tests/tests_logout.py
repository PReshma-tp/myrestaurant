from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LogoutTests(TestCase):
    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123'
        )

    def test_logout_logged_in_user(self):
        self.client.login(username='testuser', password='StrongPass123')
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)

    def test_logout_without_login(self):
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)

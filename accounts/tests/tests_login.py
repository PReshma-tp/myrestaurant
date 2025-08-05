from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginTests(TestCase):
    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.list_url = reverse('restaurants:restaurant_list')

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123'
        )

    def test_login_valid_user(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'StrongPass123'
        })
        self.assertRedirects(response, self.list_url)

    def test_login_invalid_password(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'WrongPass'
        })
        self.assertContains(response, 
                            "Please enter a correct username and password. Note that both fields may be case-sensitive.",
                            status_code=200)

    def test_login_non_existent_user(self):
        response = self.client.post(self.login_url, {
            'username': 'nouser',
            'password': 'StrongPass123'
        })
        self.assertContains(response, 
                            "Please enter a correct username and password. Note that both fields may be case-sensitive.", 
                            status_code=200)

    def test_login_blank_fields(self):
        response = self.client.post(self.login_url, {
            'username': '',
            'password': ''
        })
        self.assertContains(response, "This field is required.", status_code=200)

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationTests(TestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123'
        )

    def test_register_valid_user(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 2)
        self.assertRedirects(response, self.login_url)

    def test_register_existing_username(self):
        data = {
            'username': 'testuser',
            'email': 'unique@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertFormError(response.context['form'], 'username', 'A user with that username already exists.')

    def test_register_existing_email(self):
        data = {
            'username': 'uniqueuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertFormError(response.context['form'], 'email', "User with this Email already exists.")

    def test_register_password_mismatch(self):
        data = {
            'username': 'anotheruser',
            'email': 'another@example.com',
            'password1': 'StrongPass123',
            'password2': 'DifferentPass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertFormError(response.context['form'], 'password2', "The two password fields didn’t match.")

    def test_register_blank_email(self):
        data = {
            'username': 'blankemail',
            'email': '',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertFormError(response.context['form'], 'email', 'This field is required.')

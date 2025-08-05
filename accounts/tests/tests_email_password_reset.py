# accounts/tests/test_password_reset_email.py
import re
from django.core import mail
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

User = get_user_model()

class PasswordResetEmailTests(TestCase):
    def setUp(self):
        self.user_email = "john@doe.com"
        self.user = User.objects.create_user(
            username="john",
            email=self.user_email,
            password="Strongpass123"
        )
        self.response = self.client.post(
            reverse('accounts:password_reset'),
            {'email': self.user_email}
        )
        self.assertEqual(len(mail.outbox), 1)
        self.email = mail.outbox[0]

    def test_email_subject(self):
        expected_subject = f"Password reset on testserver"
        self.assertEqual(expected_subject, self.email.subject)

    def test_email_body_contains_reset_link(self):
        # Find reset link in the email body
        match = re.search(r"http://[^\s]+/accounts/reset/[^\s]+/[^\s]+/", self.email.body)
        self.assertIsNotNone(match, "No password reset link found in email body")
        reset_link = match.group()
        self.assertIn("/accounts/reset/", reset_link)

    def test_email_body_contains_user_info(self):
        self.assertIn(self.user.username, self.email.body)

    def test_email_to_field(self):
        self.assertEqual([self.user_email], self.email.to)

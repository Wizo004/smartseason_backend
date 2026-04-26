"""Auth + permissions tests."""
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import User

class AuthTests(APITestCase):
    def test_register_defaults_to_field_agent(self):
        r = self.client.post(reverse("register"), {
            "full_name": "Sam Agent", "email": "s@x.io", "password": "StrongPass!23",
        }, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(User.objects.get(email="s@x.io").role, "field_agent")

    def test_login_returns_jwt(self):
        User.objects.create_user(email="a@x.io", password="StrongPass!23", full_name="A")
        r = self.client.post(reverse("login"), {"email": "a@x.io", "password": "StrongPass!23"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)

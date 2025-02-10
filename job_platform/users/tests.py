# users/tests.py
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import User


class UserRegistrationTest(APITestCase):
    def test_registration(self):
        url = reverse('register')
        data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "+123456789",
            "interface_language": "ENGLISH",
            "password": "testpassword123",
            "password2": "testpassword123"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")


class LoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword123")

    def test_login_success(self):
        url = reverse('login')
        data = {"username": "testuser", "password": "testpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_failure(self):
        url = reverse('login')
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)



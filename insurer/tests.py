from django.test import TestCase
from django.urls import reverse

from .models import Insurer


class InsurerAppTest(TestCase):
    def setUp(self) -> None:
        self.insurer_model = Insurer
        self.insurer = self.insurer_model.objects.create_user(
            business_name="string",
            admin_name="string",
            business_registration_number="string",
            email="user@example.com",
            password="testing321",
            gampID="string",
        )

    def test_create_insurer(self):
        route = reverse("insurer:register_insurer")
        data = {
            "business_name": "string",
            "admin_name": "string",
            "business_registration_number": "string",
            "email": "user@example.com",
            "password": "string",
            "gampID": "string",
        }

        response = self.client.post(route, data, format="json")
        assert response.status_code == 201

    def test_login_insurer(self):
        route = reverse("insurer:login_insurer")
        data = {"email": "user@example.com", "password": "testing321"}
        response = self.client.post(route, data, format="json")
        assert response.status_code == 200

from django.test import TestCase
from django.urls import reverse
from .models import Insurer


class InsurerAppTest(TestCase):

    TEST_INSURER_USERNAME = 'Company'
    TEST_INSURER_PASSWORD = 'testing321'
    TEST_INSURER_EMAIL = 'company@gmail.com'

    def setUp(self) -> None:
        self.insurer_model = Insurer
        self.insurer = self.insurer_model.objects.create_user(username=self.TEST_INSURER_USERNAME, password=self.TEST_INSURER_PASSWORD)

    def test_create_insurer(self):
        route = reverse('insurer:register insurer')
        data = {
            "username": "TestInsurer",
            "email": "testemail@gmail.com",
            "password": "testing321"
        }
        response = self.client.post(
            route,
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_login_insurer(self):
        route = reverse("insurer:login insurer")
        data = {
            "username": self.TEST_INSURER_USERNAME,
            "password": self.TEST_INSURER_PASSWORD
        }
        response = self.client.post(
            route,
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)


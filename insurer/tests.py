from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import CustomUser
from .models import Insurer


class InsurerAppTest(TestCase):
    INSURER_DICT = {
        'business_name': 'Unyte',
        'admin_name': 'unyte_admin',
        'business_registration_number': '12345678',
        'email': 'testing321@gmail.com',
        'password': 'password'
    }

    def test_create_insurer(self) -> None:
        route = reverse('insurer:register_insurer')
        
        data = {
            'business_name': self.INSURER_DICT.get('business_name'),
            'admin_name': self.INSURER_DICT.get('admin_name'),
            'business_registration_number': self.INSURER_DICT.get('business_registration_number'),
            'email': self.INSURER_DICT.get('email'),
            'password': self.INSURER_DICT.get('password'),
        }

        response = self.client.post(route, data, format='json')
        assert response.status_code == 201
import urllib.parse

from django.test import TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404

from insurer.models import Insurer

from user.models import CustomUser


class AgentAppTestCase(TestCase):
    AGENT_DICT = {
        'first_name': 'John',
        'last_name': 'Doe',
        'middle_name': '',
        'email': 'agent_email@gmail.com',
        'password': 'testing321',
        'home_address': '10 john doe lane',
        'bank_account': '123456789',
        'bvn': '12345678901',
    }
    INSURER_DICT = {
        'business_name': 'Unyte',
        'admin_name': 'unyte_admin',
        'business_registration_number': '12345678',
        'email': 'testing321@gmail.com',
        'password': 'password',
    }

    def setUp(self) -> None:
        insurer_route = reverse('insurer:register_insurer')

        data = {
            'business_name': self.INSURER_DICT.get('business_name'),
            'admin_name': self.INSURER_DICT.get('admin_name'),
            'business_registration_number': self.INSURER_DICT.get('business_registration_number'),
            'email': self.INSURER_DICT.get('email'),
            'password': self.INSURER_DICT.get('password'),
        }

        self.client.post(insurer_route, data, format='json')

    def test_create_agent(self) -> None:
        route = reverse('agents:register_agent')
        data = {
            'first_name': self.AGENT_DICT.get('first_name'),
            'last_name': self.AGENT_DICT.get('last_name'),
            'email': self.AGENT_DICT.get('email'),
            'home_address': self.AGENT_DICT.get('home_address'),
            'bank_account': self.AGENT_DICT.get('bank_account'),
            'bvn': self.AGENT_DICT.get('bvn'),
        }

        user = get_object_or_404(CustomUser, email=self.INSURER_DICT.get('email'))
        insurer = get_object_or_404(Insurer, user=user)
        insurer_uuid = insurer.unyte_unique_insurer_id
        print(route + '?' + urllib.parse.urlencode({'invite': insurer_uuid}))

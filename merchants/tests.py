import uuid

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse_lazy

from merchants.models import Merchant
from merchants.serializers import CreateMerchantSerializer

User = get_user_model()


class CreateMerchantAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse_lazy('merchants:create-merchant')

    def test_create_merchant_success(self):
        data = {
            'name': 'Acme Corporation',
            'email_address': 'contact@acme.com',
            'password': 'securepass123',
            'short_code': 'ACME-001',
            'support_email': 'support@acme.com',
            'address': '123 Main St, Anytown, USA',
            'tax_identification_number': '123456789',
            'registration_number': 'REG123456',
        }

        response = self.client.post(self.url, data, format='json')
        __import__('pdb').set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Merchant.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)

        merchant = Merchant.objects.first()
        self.assertEqual(merchant.name, 'Acme Corporation')
        self.assertEqual(merchant.user.email, 'contact@acme.com')
        self.assertEqual(merchant.short_code, 'ACME-001')
        self.assertFalse(merchant.verified)
        self.assertFalse(merchant.kyc_verified)
        self.assertTrue(uuid.UUID(response.data['data']['tenant_id']))

    def test_create_merchant_missing_required_fields(self):
        data = {
            'name': 'Incomplete Corp',
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email_address', response.data)
        self.assertIn('password', response.data)
        self.assertIn('short_code', response.data)

    def test_create_merchant_invalid_email(self):
        data = {
            'name': 'Invalid Email Corp',
            'email_address': 'not-an-email',
            'password': 'password123',
            'short_code': 'INV-001',
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email_address', response.data)

    def test_create_merchant_duplicate_short_code(self):
        Merchant.objects.create(
            user=User.objects.create(email='existing@example.com', password='existingpass'),
            name='Existing Corp',
            short_code='DUP-001',
        )

        data = {
            'name': 'Duplicate Corp',
            'email_address': 'new@example.com',
            'password': 'newpass123',
            'short_code': 'DUP-001',
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('short_code', response.data)

    def test_create_merchant_duplicate_email(self):
        User.objects.create(email='duplicate@example.com', password='existingpass')

        data = {
            'name': 'Duplicate Email Corp',
            'email_address': 'duplicate@example.com',
            'password': 'newpass123',
            'short_code': 'DUP-002',
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user with this email already exists', response.data)

    def test_create_merchant_long_fields(self):
        data = {
            'name': 'A' * 256,  # Exceeds max_length of 255
            'email_address': 'valid@example.com',
            'password': 'password123',
            'short_code': 'A' * 11,  # Exceeds max_length of 10
            'tax_identification_number': 'A' * 41,  # Exceeds max_length of 40
            'registration_number': 'A' * 41,  # Exceeds max_length of 40
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('short_code', response.data)
        self.assertIn('tax_identification_number', response.data)
        self.assertIn('registration_number', response.data)

    def test_create_merchant_readonly_fields(self):
        data = {
            'name': 'ReadOnly Corp',
            'email_address': 'readonly@example.com',
            'password': 'password123',
            'short_code': 'READ-001',
            'tenant_id': '123e4567-e89b-12d3-a456-426614174000',  # Should be ignored
            'verified': True,
            'kyc_verified': True,
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        merchant = Merchant.objects.get(short_code='READ-001')
        self.assertNotEqual(str(merchant.tenant_id), '123e4567-e89b-12d3-a456-426614174000')
        self.assertTrue(merchant.verified)
        self.assertTrue(merchant.kyc_verified)


class CreateMerchantSerializerTestCase(TestCase):
    def test_serializer_with_valid_data(self):
        data = {
            'name': 'Tech Solutions Inc.',
            'email_address': 'info@techsolutions.com',
            'password': 'strongpass456',
            'short_code': 'TECH-001',
            'support_email': 'support@techsolutions.com',
            'address': '456 Tech Ave, Silicon Valley, CA 94000',
            'tax_identification_number': '987654321',
            'registration_number': 'TECH9876',
        }

        serializer = CreateMerchantSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_missing_required_fields(self):
        data = {
            'name': 'Incomplete Tech',
        }

        serializer = CreateMerchantSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email_address', serializer.errors)
        self.assertIn('password', serializer.errors)
        self.assertIn('short_code', serializer.errors)

    def test_serializer_invalid_email(self):
        data = {
            'name': 'Invalid Email Tech',
            'email_address': 'not-an-email',
            'password': 'password789',
            'short_code': 'INV-002',
        }

        serializer = CreateMerchantSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email_address', serializer.errors)


class MerchantModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='merchant@example.com', password='testpass')

    def test_merchant_creation(self):
        merchant = Merchant.objects.create(
            user=self.user,
            name='Test Merchant LLC',
            short_code='TEST-001',
            support_email='support@testmerchant.com',
            tax_identification_number='TIN123456',
            registration_number='REG987654',
            address='789 Business Blvd, Cityville, State 12345',
        )

        self.assertEqual(merchant.name, 'Test Merchant LLC')
        self.assertEqual(merchant.short_code, 'TEST-001')
        self.assertFalse(merchant.is_active)
        self.assertFalse(merchant.verified)
        self.assertFalse(merchant.kyc_verified)
        self.assertTrue(uuid.UUID(str(merchant.tenant_id)))

    def test_merchant_unique_constraints(self):
        Merchant.objects.create(
            user=self.user,
            name='First Merchant',
            short_code='FIRST-001',
            tax_identification_number='TIN111111',
            registration_number='REG111111',
        )

        with self.assertRaises(Exception):  # This will catch any database integrity errors
            Merchant.objects.create(
                user=User.objects.create(email='another@example.com', password='anotherpass'),
                name='Second Merchant',
                short_code='FIRST-001',  # Duplicate short_code
                tax_identification_number='TIN222222',
                registration_number='REG222222',
            )

        with self.assertRaises(Exception):
            Merchant.objects.create(
                user=User.objects.create(email='third@example.com', password='thirdpass'),
                name='Third Merchant',
                short_code='THIRD-001',
                tax_identification_number='TIN111111',  # Duplicate TIN
                registration_number='REG333333',
            )

        with self.assertRaises(Exception):
            Merchant.objects.create(
                user=User.objects.create(email='fourth@example.com', password='fourthpass'),
                name='Fourth Merchant',
                short_code='FOURTH-001',
                tax_identification_number='TIN444444',
                registration_number='REG111111',  # Duplicate registration number
            )

import os

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from user.models import CustomUser

from .utils import CustomValidationError
from .models import Agent


class CreateAgentSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=30,
        required=True,
        allow_null=False,
        allow_blank=False
    )
    last_name = serializers.CharField(
        max_length=30,
        required=True,
        allow_null=False,
        allow_blank=False
    )
    middle_name = serializers.CharField(
        allow_blank=False,
        allow_null=False
    )
    home_address = serializers.CharField(
        max_length=255,
        allow_null=False,
        allow_blank=False
    )
    email = serializers.EmailField()
    bank_account = serializers.CharField(
        min_length=10,
        max_length=10,
        allow_blank=False,
        allow_null=False
    )
    bvn = serializers.CharField(
        min_length=11,
        max_length=11,
        allow_null=False,
        allow_blank=False
    )
    # agent_gamp_id = serializers.CharField(allow_null=True,
    #                                      allow_blank=True)
    password = serializers.CharField(max_length=16, allow_blank=False, allow_null=False)

    class Meta:
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'home_address',
            'email',
            'bank_account',
            'bvn',
            # "agent_gamp_id",
            'password',
        ]

    def validate(self, attrs):
        # agent_gamp_id = attrs.get('agent_gamp_id')
        # first_name = attrs.get('first_name')
        # middle_name = attrs.get('middle_name')
        bank_account = attrs.get('bank_account')
        email = attrs.get('email')
        home_address = attrs.get('home_address')
        bvn = attrs.get('bvn')

        # print(middle_name)

        # if agent_gamp_id == '' or middle_name == '':
        #     if Agent.objects.filter(email=email).exists():
        #         raise CustomValidationError({"error": "Email already exists"})

        if CustomUser.objects.filter(email=email).exists():
            # print(CustomUser.)
            raise CustomValidationError({'error': 'Email already exists!'})

        if Agent.objects.filter(home_address=home_address).exists():
            raise CustomValidationError({'error': 'Home address already exists'})

        if Agent.objects.filter(bvn=bvn).exists():
            raise CustomValidationError({'error': 'bvn already exists'})

        if Agent.objects.filter(bank_account=bank_account).exists():
            raise CustomValidationError({'error': 'bank_account already exists'})

        #     return attrs
        #
        # else:
        #     if Agent.objects.filter(email=email).exists():
        #         raise CustomValidationError({"error": "Email already exists"})
        #
        #     if custom_user.objects.filter(email=email).exists():
        #         raise CustomValidationError({"error": "Email already exists!"})
        #
        #     if Agent.objects.filter(home_address=home_address).exists():
        #         raise CustomValidationError({"error": "Home address already exists"})
        #
        #     if Agent.objects.filter(bvn=bvn).exists():
        #         raise CustomValidationError({"error": "bvn already exists"})
        #
        #     if Agent.objects.filter(bank_account=bank_account).exists():
        #         raise CustomValidationError({"error": "bank_account already exists"})
        #
        #     pattern = f'{first_name}+{bank_account}@getgamAGENTp.com'
        #
        #     if agent_gamp_id != pattern:
        #         raise CustomValidationError({"error": "Invalid GampID"})
        #
        #     if Agent.objects.filter(agent_gamp_id=agent_gamp_id).exists():
        #         raise CustomValidationError({"error": "GampID already exists"})

        return attrs


class AgentValidateRefreshToken(serializers.Serializer):
    refresh_token = serializers.CharField()


class LoginAgentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        fields = ['email', 'password']


class LogoutAgentSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    class Meta:
        fields = ['refresh']

    def save(self):
        refresh_token = self.validated_data.get('refresh')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (ObjectDoesNotExist, TokenError) as err:
            return CustomValidationError({'error': str(err)})


class AgentOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(required=False, max_length=6)


class AgentSendNewOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = Agent
        fields = ['email']


class AgentForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        agent_email = attrs.get('email')
        if not CustomUser.objects.filter(email=agent_email, is_agent=True).exists():
            message = {'error': 'This email does not exist'}
            raise ValidationError(message)
        return attrs


class AgentForgotPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=16)
    token = serializers.CharField(min_length=1)
    id_base64 = serializers.CharField(min_length=1)
    confirm_password = serializers.CharField(max_length=16)

    class Meta:
        fields = ['new_password', 'confirm_password', 'token', 'id_base64']

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            id_base64 = attrs.get('id_base64')
            new_password = attrs.get('new_password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(id_base64))
            user = get_object_or_404(CustomUser, pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            if new_password != confirm_password:
                raise ValidationError('Password Mismatch')

            if user.check_password(raw_password=new_password):
                raise ValidationError('Password must not be the same as the last')

            user.set_password(new_password)
            user.save()

        except Exception as e:
            raise e
        return attrs


class ViewAgentDetailsSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'email',
        ]


class ViewAgentProfile(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField()
    profile_image = serializers.CharField()

    class Meta:
        fields = [
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'profile_image',
        ]

class CustomerResidentialAddress(serializers.Serializer):
    house_number = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="The number of the customer's house on their street",
        default="12"
    )
    street = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="The name of the street customer resides in",
        default="Adeola Odeku Street"
    )
    city = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="The name of the city customer resides in",
        default="Lagos"
    )
    state = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="The name of state customer currently resides in",
        default="Lagos"
    )
    postal_code = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="The postal code of home customer currently resides in",
        default="101241"
    )
    country = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="The name of country customer currently resides in",
        default="Nigeria"
    )

class CustomerDetailsSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's first name",
        default="Chukwuemeka"
    )
    last_name = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's last name",
        default="Okoro"
    )
    phone = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's phone number",
        default="08012332456"
    )
    email = serializers.EmailField(
        default="chukwuemeka.okoro@example.com"
    )
    residential_address = CustomerResidentialAddress()
    date_of_birth = serializers.DateField()
    customer_gender = serializers.CharField(
        max_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's gender",
        default="M"
    )
    occupation = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's occupation",
        default="Civil Engineer"
    )

    # TODO: Discuss with Eri on how to efficiently process send customer images to Superpool
    identity_card_img = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's identity card image",
        default="https://www.example.com/back"
    )
    utility_bill_img = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's utility bill image",
        default="https://www.example.com/back"
    )
    identity_card_type =  serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's identity card type",
        default="driver_license"
    )
    identity_card_number = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's identity card number",
        default="ARES0n0Fzews"
    )
    identity_card_expiry_date = serializers.DateField()

    class Meta:
        fields = [
            '__all__'
        ]

    def validate(self, attrs):
        attrs['date_of_birth'] = attrs['date_of_birth'].isoformat()
        attrs['identity_card_expiry_date'] = attrs['identity_card_expiry_date'].isoformat()
        return attrs

class TravelPolicyAdditionalInformationSerializer(serializers.Serializer):
    departure_date = serializers.DateField(
        help_text="Customer's travel departure date"
    )
    return_date = serializers.DateField(
        help_text="Customer's travel return date"
    )
    insurance_options = serializers.CharField(
        allow_blank=False,
        allow_null=False,
        help_text="Customer's travel insurance option",
        default="EUROPE SCHENGEN"
    )
    destination = serializers.CharField(
        allow_blank=False,
        allow_null=False,
        help_text="Customer's travel destination",
        default="France"
    )
    international_flight = serializers.BooleanField(default=False)

    class Meta:
        fields = [
            '__all__'
        ]

    def validate(self, attrs):
        attrs['departure_date'] = attrs['departure_date'].isoformat()
        attrs['return_date'] = attrs['return_date'].isoformat()

        return attrs



class TravelPolicInsuranceDetailsSerializer(serializers.Serializer):
    user_age = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Customer's age",
        default="34"
    )
    product_type = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Product type for travel",
        default="Travel"
    )
    additional_information = TravelPolicyAdditionalInformationSerializer()

    class Meta:
        fields = [
            '__all__'
        ]

class TravelPolicySerializer(serializers.Serializer):
    customer_metadata = CustomerDetailsSerializer()
    insurance_details = TravelPolicInsuranceDetailsSerializer()

    class Meta:
        fields = [
            'customer_metadata',
            'insurance_details'
        ]

class GadgetInformationSerializer(serializers.Serializer):
    more_gadget_information = serializers.CharField()
    class Meta:
        fields = ['more_gadget_information']


class GadgetUsageHistorySerializer(serializers.Serializer):
    gadget_usage_history = serializers.CharField()
    class Meta:
        fields = ['gadget_usage_history']


class GadgetPolicyAdditionalInformationSerializer(serializers.Serializer):
    gadget_type = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Gadget type or Gadget brand. E.g iPhone, Samsung, etc.",
        default = "Smartphone"
    )
    gadget_value = serializers.CharField(
        max_length=15,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        help_text="Gadget value",
        default = "1000000"
    )
    gadget_information = GadgetInformationSerializer()
    usage_history = GadgetUsageHistorySerializer()
    insurance_options = serializers.CharField(
        max_length=255,
        min_length=1,
        allow_blank=False,
        allow_null=False,
        default="Gadget Policy"
    )

class GadgetInsuranceDetailsSerializer(serializers.Serializer):
    product_type = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Product type",
        default = "Gadget"
    )
    additional_information = GadgetPolicyAdditionalInformationSerializer()

    class Meta:
        fields = [
            '__all__'
        ]

class GadgetPolicySerializer(serializers.Serializer):
    customer_metadata = CustomerDetailsSerializer()
    insurance_details = GadgetInsuranceDetailsSerializer()

    class Meta:
        fields = [
            '__all__'
        ]

class MotorPolicyAdditionalInformationSerializer(serializers.Serializer):
    vehicle_type = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Type",
        default = "Car"
    )
    vehicle_make = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Make",
        default = "Honda"
    )
    vehicle_model = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle model",
        default = "Civic"
    )
    vehicle_year = serializers.CharField(
        max_length=4,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Year",
        default = "2020"
    )
    vehicle_value = serializers.CharField(
        max_length=15,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Type",
        default = "20000.00"
    )
    vehicle_usage = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Usage",
        default = "Private"
    )
    vehicle_category = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Type",
        default = "Saloon"
    )
    insurance_options = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Insurance options",
        default = "Comprehensive"
    )

    class Meta:
        fields = [
            '__all__'
        ]

class MotorPolicyInsuranceDetailsSerializer(serializers.Serializer):
    product_type = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Product type",
        default = "Auto"
    )
    additional_information = MotorPolicyAdditionalInformationSerializer()

    class Meta:
        fields = [
            '__all__'
        ]

class MotorPolicySerializer(serializers.Serializer):
    customer_metadata = CustomerDetailsSerializer()
    insurance_details = MotorPolicyInsuranceDetailsSerializer()

    class Meta:
        fields = [
            'customer_metadata',
            'insurance_details'
        ]

class BikePolicyAdditionalInformationSerializer(serializers.Serializer):
    vehicle_type = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Type",
        default = "Bike"
    )
    vehicle_make = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Make",
        default = "Yamaha"
    )
    vehicle_model = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle model",
        default = "R1"
    )
    vehicle_year = serializers.CharField(
        max_length=4,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Year",
        default = "2021"
    )
    vehicle_value = serializers.CharField(
        max_length=15,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Type",
        default = "50000.00"
    )
    vehicle_usage = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Vehicle Usage",
        default = "Private"
    )
    insurance_options = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Insurance options",
        default = "Comprehensive"
    )

    class Meta:
        fields = [
            '__all__'
        ]

class BikePolicyInsuranceDetailsSerializer(serializers.Serializer):
    product_type = serializers.CharField(
        max_length=50,
        allow_null = False,
        allow_blank = False,
        help_text = "Product type",
        default = "Auto"
    )
    additional_information = BikePolicyAdditionalInformationSerializer()

    class Meta:
        fields = [
            '__all__'
        ]

class BikePolicySerializer(serializers.Serializer):
    customer_metadata = CustomerDetailsSerializer()
    insurance_details = BikePolicyInsuranceDetailsSerializer()

    class Meta:
        fields = [
            '__all__'
        ]


class ShipmentCarrierDetailsSerializer(serializers.Serializer):
    tracking_number = serializers.CharField(
        max_length=50,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment tracking number",
        default = "NG987654321"
    )
    service_type = serializers.CharField(
        max_length=50,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment service type",
        default = "Air Freight"
    )

    class Meta:
        fields = [
            '__all__'
        ]

class ShipmentAdditionalInformationSerializer(serializers.Serializer):
    shipment_type = serializers.CharField(
        max_length=50,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment type",
        default = "international"
    )
    shipment_value = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment value or price",
        default = "750000.50"
    )
    shipment_origin = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment origin location",
        default = "Lagos, Nigeria"
    )
    shipment_destination = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment destination location",
        default = "Accra, Ghana"
    )
    shipment_carrier = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment carrier",
        default = "XYZ Couriers"
    )
    shipment_carrier_details = ShipmentCarrierDetailsSerializer()
    exchange_rate = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment exchange rate",
        default = "750.00"
    )

    class Meta:
        fields = [
            '__all__'
        ]

class ShipmentInsuranceDetialsSerializer(serializers.Serializer):
    product_type = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Shipment exchange rate",
        default = "Cargo"
    )
    additional_information = ShipmentAdditionalInformationSerializer()

    class Meta:
        fields = [
            '__all__'
        ]

class ShipmentPolicySerializer(serializers.Serializer):
    customer_metadata = CustomerDetailsSerializer()
    insurance_details = ShipmentInsuranceDetialsSerializer()

    class Meta:
        fields = [
            '__all__'
        ]


class SellTravelPolicySerializerAdditionalInformation(serializers.Serializer):
    destination = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Travel Destination",
        default="France"
    )
    departure_date = serializers.DateField(
        help_text = "Travel departure date",
        default="2024-12-15"
    )
    return_date = serializers.DateField(
        help_text = "Travel return date",
        default="2025-01-05"
    )
    travel_purpose = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Travel purpose",
        default="Tourism"
    )
    travel_mode = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Travel mode",
        default="Air"
    )
    international_flight = serializers.BooleanField(
        help_text = "Internation flight",
        default=True
    )
    insurance_options = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Travel insurance option",
        default="TRAVELLER (WORLD WIDE)"
    )

    class Meta:
        fields = [
            '__all__'
        ]

    def validate(self, attrs):
        attrs['departure_date'] = attrs['departure_date'].isoformat()
        attrs['return_date'] = attrs['return_date'].isoformat()

        return attrs

class SellTravelPolicyActivationMetadata(serializers.Serializer):
    policy_expiry_date = serializers.DateField(
        help_text='Policy expiration date'
    )
    renew = serializers.BooleanField(
        help_text = 'Should the policy be renewed or not',
        default=False
    )

    class Meta:
        fields = [
            '__all__'
        ]

    def validate(self, attrs):
        attrs['policy_expiry_date'] = attrs['policy_expiry_date'].isoformat()
        return attrs


class SellTravelPolicySerializer(serializers.Serializer):
    customer_metadata = CustomerDetailsSerializer()
    additional_information = SellTravelPolicySerializerAdditionalInformation()
    activation_metadata = SellTravelPolicyActivationMetadata()
    quote_code =  serializers.CharField(
        max_length=200,
        allow_null=False,
        allow_blank=False,
        help_text = "Quote code generated for selling this particular policy"
    )
    product_type = serializers.CharField(
        max_length=100,
        allow_null=False,
        allow_blank=False,
        help_text = "Product type",
        default = "Travel"
    )

    class Meta:
        fields = [
            '__all__'
        ]

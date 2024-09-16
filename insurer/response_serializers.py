from django.utils import timezone
from rest_framework import serializers

from insurer.utils import FRONTED_URL


class SuccessfulCreateInsurerSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        default=1,
        help_text='insurer id',
    )
    message = serializers.CharField(
        default='Account successfully created for <insurer.business_name>',
        help_text='Success message displayed after insurer sign up'
    )

    class Meta:
        fields = [
            "id",
            "message"
        ]


class SuccessfulLoginInsurerSerializer(serializers.Serializer):
    message = serializers.CharField(
        default='OTP has been sent out to your email',
        help_text='Success message displayed after insurer receives verification OTP'
    )

    class Meta:
        fields = [
            "message"
        ]


class SuccessfulSendNewOTPSerializer(serializers.Serializer):
    message = serializers.CharField(
        default="New OTP sent out!",
        help_text="Success message displayed when new OTP has been sent out"
    )

    class Meta:
        fields = [
            "message"
        ]


class SuccessfulVerifyOTPSerializer(serializers.Serializer):
    id = serializers.CharField(
        default=1,
        help_text="id of signed in user"
    ),
    access_token = serializers.CharField(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG"
                "4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        help_text="jwt access token"
    )
    refresh_token = serializers.CharField(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFt"
                "ZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.dQw4w9WgXcQ",
        help_text="jwt refresh token"
    )

    class Meta:
        fields = [
            "id",
            "access_token",
            "refresh_token"
        ]


class SuccessfulForgotPasswordSerializer(serializers.Serializer):
    message = serializers.CharField(
        default="Confirmation email sent",
        help_text="Success message showed when the endpoint runs successfully"
    )

    class Meta:
        fields = [
            "message"
        ]


class SuccessfulResetPasswordSerializer(serializers.Serializer):
    message = serializers.CharField(
        default="Password successfully updated",
        help_text="Success message displayed when the endpoint runs successfully"
    )

    class Meta:
        fields = [
            "message"
        ]


class SuccessfulRefreshAccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG"
                "4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        help_text="jwt access token"
    )

    class Meta:
        fields = [
            "access_token"
        ]


class SuccessfulPasswordTokenCheckSerializer(serializers.Serializer):
    message = serializers.CharField(
        default="Valid Token",
        help_text="Success message"
    )
    id_base64 = serializers.CharField(
        default="",
        help_text="Example id_base64 insurer id"
    )
    token = serializers.CharField(
        default="",
        help_text="Example token"
    )

    class Meta:
        fields = [
            "message",
            "id_base64",
            "token"
        ]


class SuccessfulViewInsurerSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        default=1,
        help_text='Insurer id',
    )
    business_name = serializers.CharField(
        default="Unyte Africa",
        help_text='Insurer business name',
    )
    email = serializers.EmailField(
        default="yourbusinessemail@gmail.com",
        help_text="Insurer email"
    )

    class Meta:
        fields = [
            'id',
            'business_name',
            'email',
        ]


class AllAgentsSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        default=1,
        help_text='Insurer id',
    )
    first_name = serializers.CharField(
        default="first_name",
        help_text="Agent first name"
    )
    last_name = serializers.CharField(
        default="last_name",
        help_text="Agent last name"
    )
    email = serializers.EmailField(
        default="yourbusinessemail@gmail.com",
        help_text="Agent email"
    )

    class Meta:
        fields = [
            'id',
            'first_name',
            'last_name',
            'email'
        ]


class SuccessfulListAllAgentsSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        default=1,
        help_text='Insurer id',
    )
    first_name = serializers.CharField(
        default="first_name",
        help_text="Agent first name"
    )
    last_name = serializers.CharField(
        default="last_name",
        help_text="Agent last name"
    )
    email = serializers.EmailField(
        default="yourbusinessemail@gmail.com",
        help_text="Agent email"
    )

    class Meta:
        fields = [
            'id',
            'first_name',
            'last_name',
            'email'
        ]


class ProductPolicyTypeSerializer(serializers.Serializer):
    name = serializers.CharField(
        default="Basic",
        help_text="product/policy type name"
    )
    premium = serializers.DecimalField(
        default="1000.00",
        max_digits=10,
        decimal_places=2,
        help_text="product/policy price"
    )
    flat_fee = serializers.CharField(
        default="YES",
        help_text="product/policy type flat tee value"
    )

    class Meta:
        fields = [
            "name",
            "premium",
            "flat_fee"
        ]


class SuccessfulInsurerProductsSerializer(serializers.Serializer):
    product = serializers.CharField(
        default="Product Plan",
        help_text="Product name"
    )
    product_category = serializers.CharField(
        default="DEVICES",
        help_text="product category"
    )
    valid_from = serializers.DateTimeField(
        default=timezone.now(),
        help_text="date at which policy is valid from"
    )
    valid_to = serializers.DateTimeField(
        default=timezone.now(),
        help_text="date at which policy is valid to"
    )
    product_types = ProductPolicyTypeSerializer(many=True)

    class Meta:
        fields = [
            "product",
            "product_category",
            "valid_from",
            "valid_to",
            "product_types"
        ]


class PoliciesTypeSerializer(serializers.Serializer):
    name = serializers.CharField(
        default="Basic",
        help_text="policy type name"
    )
    premium = serializers.DecimalField(
        default="1000.00",
        max_digits=10,
        decimal_places=2,
        help_text="policy price"
    )
    flat_fee = serializers.CharField(
        default="YES",
        help_text="policy type flat tee value"
    )

    class Meta:
        fields = [
            "name",
            "premium",
            "flat_fee"
        ]


class InsurerAgentPoliciesSerializer(serializers.Serializer):
    policy_name = serializers.CharField(
        default="Policy Plan",
        help_text="policy name"
    )
    policy_category = serializers.CharField(
        default="DEVICES",
        help_text="policy category"
    )
    policy_types = PoliciesTypeSerializer(many=True)

    class Meta:
        fields = [
            'policy_name',
            'policy_category'
        ]


class SuccessfulInsurerPoliciesSerializer(serializers.Serializer):
    agents = serializers.CharField(
        default="John Doe",
        help_text="agent's details [first_name + last_name]"
    )
    policies_sold = InsurerAgentPoliciesSerializer(many=True)

    class Meta:
        fields = [
            'agents',
            'policies_sold'
        ]


class SuccessfulInsurerAgentSignupSerializer(serializers.Serializer):
    message = serializers.CharField(
        default=f'http://{FRONTED_URL}/agent/sign-up?invite=<insurer.unyte_unique_insurer_id>',
        help_text="success message after email has been sent to agent(s) email(s)"
    )

    class Meta:
        fields = [
            'message'
        ]


class SuccessfulInsurerAgentSignupCSVSerializer(serializers.Serializer):
    message = serializers.CharField(
        default=f'Successfully sent out invite links to <number_of_agents> agent(s)',
        help_text="success message after email has been sent to agent(s) email(s)"
    )

    class Meta:
        fields = [
            'message'
        ]



class SuccessfulCreateProductSerializer(serializers.Serializer):
    policy = serializers.CharField(
        default="Policy Plan",
        help_text="policy name"
    )
    policy_category = serializers.CharField(
        default="DEVICES",
        help_text="policy category"
    )
    valid_from = serializers.DateTimeField(
        default=timezone.now(),
        help_text="date at which policy is valid from"
    )
    valid_to = serializers.DateTimeField(
        default=timezone.now(),
        help_text="date at which policy is valid to"
    )
    policy_type = ProductPolicyTypeSerializer(many=True)

    class Meta:
        fields = [
            'policy',
            'policy_category',
            'valid_from',
            'valid_to',
            'policy_type'
        ]


class SuccessfulCreateProductForPolicySerializer(serializers.Serializer):
    message = serializers.CharField(
        default="A new product has been added to <policy.name>",
        help_text='success message when new product type has been added to product'
    )

    class Meta:
        fields = [
            'message'
        ]

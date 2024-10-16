from django.utils import timezone

from rest_framework import serializers

from agents.utils import FRONTED_URL


class SuccessfulCreateAgentSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        default=1,
        help_text="agent id",
    )
    message = serializers.CharField(
        default="Account successfully created for <agent.first_name> <agent.last_name>",
        help_text="Success message displayed after agent sign up",
    )

    class Meta:
        fields = ["id", "message"]


class SuccessfulLoginAgentSerializer(serializers.Serializer):
    message = serializers.CharField(
        default="OTP has been sent out to your email",
        help_text="Success message displayed after agent receives verification OTP",
    )

    class Meta:
        fields = ["message"]


class AgentSuccessfulSendNewOTPSerializer(serializers.Serializer):
    message = serializers.CharField(
        default="New OTP sent out!", help_text="Success message displayed when new OTP has been sent out"
    )

    class Meta:
        fields = ["message"]


class AgentSuccessfulVerifyOTPSerializer(serializers.Serializer):
    login_status = (serializers.BooleanField(default=True, help_text="login status of agent"),)
    access_token = serializers.CharField(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG"
        "4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        help_text="jwt access token",
    )
    refresh_token = serializers.CharField(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFt"
        "ZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.dQw4w9WgXcQ",
        help_text="jwt refresh token",
    )

    class Meta:
        fields = ["id", "access_token", "refresh_token"]


class AgentSuccessfulForgotPasswordSerializer(serializers.Serializer):
    message = serializers.CharField(
        default="Confirmation email sent", help_text="Success message showed when the endpoint runs successfully"
    )

    class Meta:
        fields = ["message"]


class AgentSuccessfulResetPasswordSerializer(serializers.Serializer):
    message = serializers.CharField(
        default="Password successfully updated",
        help_text="Success message displayed when the endpoint runs successfully",
    )

    class Meta:
        fields = ["message"]


class AgentSuccessfulRefreshAccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG"
        "4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        help_text="jwt access token",
    )

    class Meta:
        fields = ["access_token"]


class AgentSuccessfulPasswordTokenCheckSerializer(serializers.Serializer):
    message = serializers.CharField(default="Valid Token", help_text="Success message")
    id_base64 = serializers.CharField(default="", help_text="Example id_base64 insurer id")
    token = serializers.CharField(default="", help_text="Example token")

    class Meta:
        fields = ["message", "id_base64", "token"]


class SuccessfulViewAgentSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        default=1,
        help_text="Insurer id",
    )
    first_name = serializers.CharField(
        default="John",
        help_text="Agent first name",
    )
    last_name = serializers.CharField(
        default="Doe",
        help_text="Agent last name",
    )
    middle_name = serializers.CharField(
        default="L",
        help_text="Agent middle name",
    )
    email = serializers.EmailField(default="youragent@gmail.com", help_text="Agent email")

    class Meta:
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "email",
        ]


class SuccessfulViewAgentProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(default="youragent@gmail.com", help_text="Agent email")
    first_name = serializers.CharField(
        default="John",
        help_text="Agent first name",
    )
    last_name = serializers.CharField(
        default="Doe",
        help_text="Agent last name",
    )
    middle_name = serializers.CharField(
        default="L",
        help_text="Agent middle name",
    )
    profile_image = serializers.URLField(default="", help_text="url for agent profile picture")

    class Meta:
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "email",
        ]


class SuccessfulAgentSellProductSerializer(serializers.Serializer):
    message = serializers.CharField(default="You have successfully sold this product", help_text="successful message")

    class Meta:
        fields = ["message"]


class AgentProductPolicyTypeSerializer(serializers.Serializer):
    name = serializers.CharField(default="Basic", help_text="product/policy type name")
    premium = serializers.DecimalField(
        default="1000.00", max_digits=10, decimal_places=2, help_text="product/policy price"
    )
    flat_fee = serializers.CharField(default="YES", help_text="product/policy type flat tee value")

    class Meta:
        ref_name = "agents"
        fields = ["name", "premium", "flat_fee"]


class SuccessfulInsurerAgentProductsSerializer(serializers.Serializer):
    product = serializers.CharField(default="Product Plan", help_text="Product name")
    product_category = serializers.CharField(default="DEVICES", help_text="product category")
    valid_from = serializers.DateTimeField(default=timezone.now(), help_text="date at which policy is valid from")
    valid_to = serializers.DateTimeField(default=timezone.now(), help_text="date at which policy is valid to")
    product_types = AgentProductPolicyTypeSerializer(many=True)

    class Meta:
        fields = ["product", "product_category", "valid_from", "valid_to", "product_types"]


class AgentPoliciesTypeSerializer(serializers.Serializer):
    name = serializers.CharField(default="Basic", help_text="policy type name")
    premium = serializers.DecimalField(default="1000.00", max_digits=10, decimal_places=2, help_text="policy price")
    flat_fee = serializers.CharField(default="YES", help_text="policy type flat tee value")

    class Meta:
        fields = ["name", "premium", "flat_fee"]


class AgentPoliciesSerializer(serializers.Serializer):
    policy_name = serializers.CharField(default="Policy Plan", help_text="policy name")
    policy_category = serializers.CharField(default="DEVICES", help_text="policy category")
    policy_types = AgentPoliciesTypeSerializer(many=True)

    class Meta:
        fields = ["policy_name", "policy_category"]


class SuccessfulInsurerAgentSignupSerializer(serializers.Serializer):
    message = serializers.CharField(
        default=f"http://{FRONTED_URL}/agent/sign-up?invite=<insurer.unyte_unique_insurer_id>",
        help_text="success message after email has been sent to agent(s) email(s)",
    )

    class Meta:
        fields = ["message"]


class SuccessfulCreateProductSerializer(serializers.Serializer):
    policy = serializers.CharField(default="Policy Plan", help_text="policy name")
    policy_category = serializers.CharField(default="DEVICES", help_text="policy category")
    valid_from = serializers.DateTimeField(default=timezone.now(), help_text="date at which policy is valid from")
    valid_to = serializers.DateTimeField(default=timezone.now(), help_text="date at which policy is valid to")
    policy_type = AgentProductPolicyTypeSerializer(many=True)

    class Meta:
        fields = ["policy", "policy_category", "valid_from", "valid_to", "policy_type"]


class SuccessfulCreateProductForPolicySerializer(serializers.Serializer):
    message = serializers.CharField(
        default="A new product has been added to <policy.name>",
        help_text="success message when new product type has been added to product",
    )

    class Meta:
        fields = ["message"]

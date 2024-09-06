from rest_framework import serializers


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
    message =serializers.CharField(
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


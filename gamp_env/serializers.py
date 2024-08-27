from rest_framework import serializers
from .models import GampArbitraryClaim, GampArbitraryUser, GampArbitraryDevice, GampArbitraryPolicy, \
    GampArbitraryProduct, UserPolicy


class GampDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GampArbitraryDevice
        fields = [
            'device_type',
            'model',
        ]


class GampUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GampArbitraryUser
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'email'
        ]


class GampClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = GampArbitraryClaim
        fields = [
            'customer',
            'device',
            'description',
            'issue',
            'address',
            'technician_address',
        ]


class GampArbitraryPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = GampArbitraryPolicy
        fields = [
            'policy_uuid',
            'policy_name',
            'description',
            'insurer'
        ]


class GampArbitratyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = GampArbitraryProduct
        fields = [
            "premium",
            "product_name",
            "flat_fee"
        ]


class UserPolicyProductTypeSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=240,
                                         help_text="Name of product under the policy that user wants to purchase")
    premium = serializers.DecimalField(max_digits=10,
                                       decimal_places=2,
                                       help_text="Price of the product")
    flat_fee = serializers.CharField(max_length=3,
                                     help_text="Flat fee of policy customer wants to purchase")


class UserPolicySerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=240,
                                   help_text="User first name")
    last_name = serializers.CharField(max_length=240,
                                   help_text="User last name")
    policy = serializers.CharField(max_length=240,
                                   help_text="Policy user wants to buy")
    product_type = UserPolicyProductTypeSerializer(many=True)


# class ViewAritraryPolicySerializer(serializers.ModelSerializer):
#     product = GampArbitratyProductSerializer()
#     policy = GampArbitraryPolicySerializer()
#
#     class Meta:
#         model = GampPolicyProducts
#         fields = [
#             "product",
#             "policy"
#         ]

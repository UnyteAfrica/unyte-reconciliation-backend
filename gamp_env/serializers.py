from rest_framework import serializers
from .models import GampArbitraryClaim, GampArbitraryUser, GampArbitraryDevice


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

    def create(self, validated_data):
        claim = GampArbitraryClaim.objects.create(**validated_data)
        return claim

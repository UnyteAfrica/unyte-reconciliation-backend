import re

from insurer.models import Insurer
from .models import Agent
from rest_framework import serializers


class CreateAgentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30,
                                       allow_null=False,
                                       allow_blank=False)
    last_name = serializers.CharField(max_length=30,
                                      allow_null=False,
                                      allow_blank=False)
    middle_name = serializers.CharField(max_length=30,
                                        allow_blank=False,
                                        allow_null=False)
    home_address = serializers.CharField(max_length=255,
                                         allow_null=False,
                                         allow_blank=False)
    email = serializers.EmailField()
    bank_account = serializers.CharField(max_length=10,
                                         allow_blank=False,
                                         allow_null=False)
    bvn = serializers.CharField(max_length=11,
                                allow_null=False,
                                allow_blank=False)
    affiliated_company = serializers.CharField(allow_blank=False,
                                               allow_null=False)
    agent_gampID = serializers.CharField(allow_null=True,
                                         allow_blank=True)
    password = serializers.CharField(max_length=16,
                                     allow_blank=False,
                                     allow_null=False)

    class Meta:
        model = Agent
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "home_address",
            "email",
            "bank_account",
            "bvn",
            "affiliated_company",
            "agent_gampID",
            "password"
        ]

    def validate_agent_gampID(self, validated_data):
        agent_gampID = validated_data
        if agent_gampID == '':
            return
        pattern = r'^[a-zA-Z0-9._%+-]+[+][0-9]{10}@getgamp\.com$'
        if not re.match(pattern, agent_gampID):
            return "Invalid gampID"

    def create(self, validated_data):
        affiliated_company = validated_data.get('affiliated_company')

        insurer = Insurer.objects.filter(business_name=affiliated_company).exists()

        if not insurer:
            return "Affiliated company does not exist"

        insurer = Insurer.objects.get(business_name=affiliated_company)
        validated_data['affiliated_company'] = insurer

        agent = Agent.objects.create_user(**validated_data)
        agent.save()
        return agent

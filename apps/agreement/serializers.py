from agreement.models import LaborFeeLevel
from rest_framework import serializers


class LaborFeeLevelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaborFeeLevel
        fields = ['id', 'level']

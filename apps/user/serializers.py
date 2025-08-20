from django.core.cache import cache

from user.models import Doctor
from utils.base import PhoneValidator
from rest_framework import serializers

from utils.ym_restframework.exceptions import TextValidationError


class DoctorSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    phone = serializers.CharField(min_length=11, max_length=11, validators=[PhoneValidator()])

    @property
    def verbose_data(self):
        data = super().data
        new_data = {}
        for k, v in data.items():
            field = self.Meta.model._meta.get_field(k)
            new_data[field.verbose_name] = v
        return new_data

    class Meta:
        model = Doctor
        exclude = ['created_at', 'updated_at']


class DoctorEmbededSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(min_length=11, max_length=11, validators=[PhoneValidator()])

    class Meta:
        model = Doctor
        fields = ['phone', 'name', 'hospital']


class DoctorRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'state', 'cause', 'hospital', ]
        extra_kwargs = {field: {'read_only': True} for field in fields}


class DoctorCreateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6, help_text="验证码", required=True, write_only=True)
    openid = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(required=True, write_only=True, max_length=11, min_length=11)
    pic = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')
        history_code = cache.get(f'sms:code:{attrs["phone"]}:latestCode')
        # if not history_code or (code != history_code):
        #     raise TextValidationError(detail="验证码错误或已过期")
        return attrs

    class Meta:
        model = Doctor
        fields = ["code", "openid", "phone", "pic"]
        extra_kwargs = {field: {'required': True, "write_only": True} for field in fields}

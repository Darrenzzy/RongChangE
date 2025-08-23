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
        fields = ['id', 'openid', 'phone', 'name', 'gender', 'birthday', 'hospital', 'province', 
                 'region', 'precinct', 'pic', 'sign_img', 'state', 'cause', 'bank', 
                 'bank_card_number', 'bank_operation_name', 'card_number', 'last_login', 
                 'is_subscribe', 'created_at', 'updated_at']
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


class DoctorProfileUpdateSerializer(serializers.Serializer):
    """用于更新医生完整资料的序列化器"""
    code = serializers.CharField(max_length=6, min_length=6, help_text="验证码", required=True, write_only=True)
    openid = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(required=True, write_only=True, max_length=11, min_length=11)
    name = serializers.CharField(max_length=10, required=False)
    gender = serializers.CharField(max_length=10, required=False)
    birthday = serializers.DateField(required=False)
    card_number = serializers.CharField(required=False)
    bank = serializers.CharField(max_length=100, required=False)
    bank_card_number = serializers.CharField(required=False)
    bank_operation_name = serializers.CharField(max_length=50, required=False)
    hospital = serializers.CharField(max_length=30, required=False)
    province = serializers.CharField(max_length=30, required=False)
    region = serializers.CharField(max_length=30, required=False)
    precinct = serializers.CharField(max_length=30, required=False)
    pic = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')
        history_code = cache.get(f'sms:code:{attrs["phone"]}:latestCode')
        # if not history_code or (code != history_code):
        #     raise TextValidationError(detail="验证码错误或已过期")
        return attrs

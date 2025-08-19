from hashlib import sha256

from django.core.cache import cache
from rest_framework import serializers

from utils.ym_restframework.exceptions import TextValidationError
from works.models import Case, MedCase, Disease, Question, Item


class CreateCaseSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = self.context["request"].user
        throttle_key = f"case:commit:{user.pk}"
        throttle = cache.get(throttle_key)
        if throttle:
            raise TextValidationError("提交太频繁了，请稍后再试")

        sha256_hash = sha256(str(validated_data).encode()).hexdigest()
        sha256_key = f"case:commit:sha256:{user.pk}:{sha256_hash}"
        is_exists = cache.get(sha256_key)
        if is_exists:
            raise TextValidationError("您已提交成功过该数据，请勿重复提交，谢谢~")
        _category = validated_data.get("category")
        if _category not in ["SLE/LN", "MG"]:
            raise TextValidationError(f"素材类型-{_category}非法，请调整~")

        instance = super().create(validated_data)

        instance.author = user
        instance.hospital = user.hospital
        instance.phone = user.phone
        instance.save()
        cache.set(throttle_key, True, 60)
        cache.set(sha256_key, True, None)
        return instance

    class Meta:
        model = Case
        fields = ["sex", "age", "category", "case_now", "sle", "case_time", "history_scheme", "now_scheme", "metrics"]
        extra_kwargs = {
            "category": {"write_only": True, "read_only": False},
            **{field: {'required': True, "write_only": True} for field in fields if field != "category"}
        }


class ListCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ["id", "created_at", "category", ]


class CaseAndMedCaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    category = serializers.SerializerMethodField()

    @staticmethod
    def get_category(instance):
        return str(getattr(instance, "category", "")) or str(getattr(instance, "disease", ""))


class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ("id", "title")


class QuestionSerializer(serializers.ModelSerializer):
    items = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Question
        exclude = ("created_at", "updated_at", "is_use", "order")


class DiseaseRetrieveSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    @staticmethod
    def get_questions(obj):
        return QuestionSerializer(obj.questions.filter(is_use=True).all(), many=True).data

    class Meta:
        model = Disease
        exclude = ("created_at", "updated_at", "order")


class MedCaseSerializer(serializers.ModelSerializer):
    disease = serializers.PrimaryKeyRelatedField(queryset=Disease.objects.filter(is_use=True), required=True)
    data = serializers.JSONField()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = MedCase
        fields = ("disease", "data")

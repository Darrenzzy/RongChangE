#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: serializers.py

@author: 'ovan'

@mtime: '2024/7/30'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from rest_framework import serializers

from survey.models import DiseasesCategory, CommitLog, QuestionBank, Option


class NestOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "title", ]


class RetrieveQuestionBankSerializer(serializers.ModelSerializer):
    options = NestOptionSerializer(many=True)

    class Meta:
        model = QuestionBank
        fields = ["id", "title", "category", "scope", "options", ]


class ListDiseasesCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseasesCategory
        fields = ["id", "title", ]


class CreateQuestionBankSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    data = serializers.JSONField()
    '''p = [
        {
            "id": 10,
            "scope": "患者的病程或疾病阶段",
            "kind": "S",
            "title": "您诊治的患者中，缓解期患者占比是多少？",
            "options": [
                {
                    "id": 45,
                    "title": "10%-20%"
                }
            ]
        },
        {
            "id": 12,
            "scope": "患者的病程或疾病阶段",
            "kind": "P",
            "title": "您认为病程管理对类风湿性关节炎患者生活质量影响有多大？（1-5分）",
            "options": [
                {
                    "id": 58,
                    "title": "5分"
                }
            ]
        },
        {
            "id": 13,
            "scope": "既往用药习惯",
            "kind": "S",
            "title": "您诊治的患者中，使用非甾体抗炎药（NSAIDs）治疗的占比是多少？",
            "options": [
                {
                    "id": 62,
                    "title": "40%-50%"
                }
            ]
        },
        {
            "id": 16,
            "scope": "既往用药习惯",
            "kind": "T",
            "title": "请按类风湿性关节炎药物的使用频率排序（1为最常用）",
            "options": [
                {
                    "id": 0,
                    "title": "我是自由输入的填空题：传统合成DMARDs（csDMARDs）"
                }
            ]
        },
        {
            "id": 19,
            "scope": "药物经济学",
            "kind": "D",
            "title": "您认为哪些因素会影响类风湿性关节炎的治疗费用？",
            "options": [
                {
                    "id": 92,
                    "title": "保险覆盖范围"
                },
                {
                    "id": 93,
                    "title": "其他"
                }
            ]
        },
        {
            "id": 21,
            "scope": "药物经济学",
            "kind": "T",
            "title": "请按类风湿性关节炎治疗费用的影响因素排序（1为最重要）",
            "options": [
                {
                    "id": 0,
                    "title": "我是自由输入的填空题"
                }
            ]
        },
        {
            "id": 24,
            "scope": "对既往标准治疗药物的疗效的评价",
            "kind": "D",
            "title": "您认为哪些标准治疗药物的疗效较好？",
            "options": [
                {
                    "id": 114,
                    "title": "传统合成DMARDs（csDMARDs）"
                },
                {
                    "id": 115,
                    "title": "生物DMARDs（bDMARDs）"
                }
            ]
        },
        {
            "id": 30,
            "scope": "流行病学",
            "kind": "S",
            "title": "您诊治的患者中，初次确诊时的平均年龄是多少？",
            "options": [
                {
                    "id": 148,
                    "title": "60岁以上"
                }
            ]
        },
        {
            "id": 39,
            "scope": "既往用药习惯",
            "kind": "D",
            "title": "您认为哪些药物的副作用较小？",
            "options": [
                {
                    "id": 189,
                    "title": "传统合成DMARDs（csDMARDs）"
                },
                {
                    "id": 190,
                    "title": "生物DMARDs（bDMARDs）"
                }
            ]
        },
        {
            "id": 42,
            "scope": "既往用药习惯",
            "kind": "P",
            "title": "您认为药物副作用对类风湿性关节炎患者生活质量影响有多大？（1-5分）",
            "options": [
                {
                    "id": 204,
                    "title": "1分"
                }
            ]
        }
    ]'''

    category = serializers.PrimaryKeyRelatedField(queryset=DiseasesCategory.objects.filter(is_use=True))

    class Meta:
        model = CommitLog
        fields = ["user", "data", 'category']


class ListMyHistoryViewSetSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = CommitLog
        fields = ["id", "category", "created_at", ]


class CreateCommitLogSerializer(serializers.ModelSerializer):
    """
    外部API提交调研记录的序列化器
    """
    category_id = serializers.IntegerField(help_text="疾病分类ID")
    user_id = serializers.IntegerField(help_text="医生用户ID")
    hospital = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text="医院名称")
    phone = serializers.CharField(max_length=11, required=False, allow_blank=True, help_text="手机号")
    level_id = serializers.IntegerField(required=False, allow_null=True, help_text="劳务费档位ID")
    state_id = serializers.IntegerField(required=False, allow_null=True, help_text="状态ID")
    payment_time = serializers.DateTimeField(required=False, allow_null=True, help_text="支付时间")
    payment_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=0.00, help_text="支付金额"
    )
    data = serializers.JSONField(help_text="提交的答题数据")

    class Meta:
        model = CommitLog
        fields = [
            "category_id", "user_id", "hospital", "phone", "level_id", 
            "state_id", "payment_time", "payment_amount", "data"
        ]

    def validate_category_id(self, value):
        """验证疾病分类是否存在且启用"""
        if not DiseasesCategory.objects.filter(id=value, is_use=True).exists():
            raise serializers.ValidationError("疾病分类不存在或未启用")
        return value

    def validate_user_id(self, value):
        """验证用户是否存在"""
        from user.models import Doctor
        if not Doctor.objects.filter(id=value).exists():
            raise serializers.ValidationError("用户不存在")
        return value

    def validate_level_id(self, value):
        """验证劳务费档位是否存在"""
        if value is not None:
            from agreement.models import LaborFeeLevel
            if not LaborFeeLevel.objects.filter(id=value).exists():
                raise serializers.ValidationError("劳务费档位不存在")
        return value

    def validate_state_id(self, value):
        """验证状态是否存在"""
        if value is not None:
            from works.models import WorksState
            if not WorksState.objects.filter(id=value).exists():
                raise serializers.ValidationError("状态不存在")
        return value

    def create(self, validated_data):
        """创建提交记录"""
        return CommitLog.objects.create(
            category_id=validated_data['category_id'],
            user_id=validated_data['user_id'],
            hospital=validated_data.get('hospital'),
            phone=validated_data.get('phone'),
            level_id=validated_data.get('level_id'),
            state_id=validated_data.get('state_id'),
            payment_time=validated_data.get('payment_time'),
            payment_amount=validated_data.get('payment_amount', 0.00),
            data=validated_data['data'],
        )

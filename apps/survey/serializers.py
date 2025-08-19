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

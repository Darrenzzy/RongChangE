#!/bin/bash

echo "=========================================="
echo "使用真实题库数据测试API"
echo "=========================================="
echo "分类: 类风湿关节炎 (category_id: 7)"
echo "包含4种题目类型: 单选(S)、多选(D)、评分(P)、排序(T)"
echo ""

# 使用真实的题库数据测试API

curl -X POST http://127.0.0.1:8009/api/survey/external/commitlog/ \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 7,
    "user_id": 597,
    "hospital": "测试医院",
    "phone": "13800138000",
    "level_id": null,
    "state_id": null,
    "payment_time": null,
    "payment_amount": 0.00,
    "data": [
      {
        "id": 223,
        "title": "您所在地区类风湿性关节炎的患病率是多少？",
        "scope": "流行病学",
        "kind": "S",
        "options": [
          {
            "id": 1111,
            "title": "2%-3%"
          }
        ]
      },
      {
        "id": 224,
        "title": "您认为类风湿性关节炎的主要致病因素有哪些？",
        "scope": "流行病学",
        "kind": "D",
        "options": [
          {
            "id": 1114,
            "title": "遗传因素"
          },
          {
            "id": 1116,
            "title": "免疫系统问题"
          }
        ]
      },
      {
        "id": 227,
        "title": "您认为早期诊断对类风湿性关节炎的治疗效果影响有多大？（1-5分）",
        "scope": "流行病学", 
        "kind": "P",
        "options": [
          {
            "id": 1127,
            "title": "4分"
          }
        ]
      },
      {
        "id": 226,
        "title": "请按类风湿性关节炎的常见症状出现频率排序题（1为最常见）：关节疼痛、晨僵、乏力、发热",
        "scope": "流行病学",
        "kind": "T",
        "options": [
          {
            "id": 0,
            "title": "关节疼痛1、晨僵2、乏力3、发热4"
          }
        ]
      },
      {
        "id": 233,
        "title": "您诊治的患者中，使用非甾体抗炎药（NSAIDs）治疗的占比是多少？",
        "scope": "既往用药习惯",
        "kind": "S", 
        "options": [
          {
            "id": 1152,
            "title": "40%-50%"
          }
        ]
      },
      {
        "id": 234,
        "title": "您常使用哪些药物治疗类风湿性关节炎？",
        "scope": "既往用药习惯",
        "kind": "D",
        "options": [
          {
            "id": 1154,
            "title": "传统合成DMARDs（csDMARDs）"
          },
          {
            "id": 1155,
            "title": "生物DMARDs（bDMARDs）"
          }
        ]
      },
      {
        "id": 242,
        "title": "您认为降低治疗费用对提高患者依从性影响有多大？（1-5分）",
        "scope": "药物经济学",
        "kind": "P",
        "options": [
          {
            "id": 1186,
            "title": "4分"
          }
        ]
      },
      {
        "id": 244,
        "title": "您认为哪些标准治疗药物的疗效较好？",
        "scope": "既往标准治疗药物的疗效评价",
        "kind": "D", 
        "options": [
          {
            "id": 1194,
            "title": "生物DMARDs（bDMARDs）"
          },
          {
            "id": 1195,
            "title": "靶向合成DMARDs（tsDMARDs）"
          }
        ]
      },
      {
        "id": 250,
        "title": "您诊治的患者中，初次确诊时的平均年龄是多少？",
        "scope": "流行病学",
        "kind": "S",
        "options": [
          {
            "id": 1220,
            "title": "50-60岁"
          }
        ]
      },
      {
        "id": 262,
        "title": "您认为药物副作用对类风湿性关节炎患者生活质量影响有多大？（1-5分）",
        "scope": "既往用药习惯",
        "kind": "P",
        "options": [
          {
            "id": 1263,
            "title": "3分"
          }
        ]
      }
    ]
  }'

echo ""
echo ""
echo "=========================================="
echo "API测试说明"
echo "=========================================="
echo "本次测试包含了真实的题库数据:"
echo "✅ 单选题(S): 4道 - 患病率、用药占比、确诊年龄等"
echo "✅ 多选题(D): 3道 - 致病因素、治疗药物、疗效评价等"  
echo "✅ 评分题(P): 3道 - 早期诊断影响、费用影响、副作用影响等"
echo "✅ 排序题(T): 1道 - 症状频率排序"
echo ""
echo "题目涵盖范围:"
echo "- 流行病学"
echo "- 既往用药习惯" 
echo "- 药物经济学"
echo "- 既往标准治疗药物的疗效评价"
echo ""
echo "所有题目ID和选项ID都是从数据库中真实查询获得！"
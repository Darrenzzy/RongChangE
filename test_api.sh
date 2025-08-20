#!/bin/bash

# 测试外部API提交调研记录
echo "=========================================="
echo "测试外部API提交调研记录"
echo "=========================================="
echo "API地址: POST http://127.0.0.1:8000/api/survey/external/commitlog/"
echo ""

# 测试数据
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
        "id": 1,
        "title": "测试题目1",
        "scope": "测试范围",
        "kind": "S",
        "options": [
          {
            "id": 1,
            "title": "选项A"
          }
        ]
      },
      {
        "id": 2,
        "title": "测试题目2",
        "scope": "测试范围", 
        "kind": "D",
        "options": [
          {
            "id": 2,
            "title": "选项B"
          },
          {
            "id": 3,
            "title": "选项C"
          }
        ]
      }
    ]
  }'

echo ""
echo ""
echo "=========================================="
echo "API文档说明："
echo "=========================================="
echo "✅ 特性:"
echo "- 无需签名认证（已添加到签名验证白名单）"
echo "- 无需用户认证（专为外部系统设计）"
echo "- 自动验证关联数据的有效性"
echo "- 完整的错误处理和日志记录"
echo ""
echo "📋 必填参数:"
echo "- category_id: 疾病分类ID (需存在且is_use=True)"
echo "- user_id: 医生用户ID (需存在于user_doctor表)"
echo "- data: 提交的答题数据 (JSON数组格式)"
echo ""
echo "📋 可选参数:"
echo "- hospital: 医院名称"
echo "- phone: 手机号"
echo "- level_id: 劳务费档位ID"
echo "- state_id: 状态ID" 
echo "- payment_time: 支付时间"
echo "- payment_amount: 支付金额"
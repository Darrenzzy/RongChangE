#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试外部API提交survey_commitlog数据的脚本
"""
import json
import requests
from datetime import datetime

# API配置
API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = "/api/survey/external/commitlog/"

def test_commitlog_api():
    """测试提交调研记录API"""
    
    # 测试数据 - 请根据实际数据库情况调整ID值
    test_data = {
        "category_id": 1,  # 需要确保数据库中存在ID为1的疾病分类，且is_use=True
        "user_id": 1,      # 需要确保数据库中存在ID为1的医生用户
        "hospital": "测试医院",
        "phone": "13800138000",
        "level_id": None,  # 可选，需要对应agreement_laborfee_level表中的ID
        "state_id": None,  # 可选，需要对应works_worksstate表中的ID
        "payment_time": None,  # 可选，格式: "2024-08-20T10:00:00Z"
        "payment_amount": 0.00,
        "data": [
            {
                "id": 1,
                "title": "测试题目1",
                "scope": "测试范围",
                "kind": "S",  # S=单选题, D=多选题, P=评分题, T=排序题
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
                "kind": "D",  # 多选题可以有多个选项
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
    }
    
    url = f"{API_BASE_URL}{API_ENDPOINT}"
    headers = {
        'Content-Type': 'application/json',
    }
    
    try:
        print(f"正在测试API: {url}")
        print(f"提交数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            print("✅ API测试成功！")
            result = response.json()
            if result.get('code') == 200:
                print(f"✅ 数据提交成功，记录ID: {result['data']['id']}")
            else:
                print(f"❌ 业务逻辑错误: {result.get('msg')}")
        else:
            print("❌ API测试失败")
            if response.status_code == 400:
                error_info = response.json()
                print(f"错误详情: {error_info}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请确保Django服务器正在运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def print_api_documentation():
    """打印API使用文档"""
    print("=" * 80)
    print("外部API提交调研记录文档")
    print("=" * 80)
    print(f"API地址: POST {API_BASE_URL}{API_ENDPOINT}")
    print("\n✅ 特性:")
    print("- 无需签名认证（已添加到签名验证白名单）")
    print("- 无需用户认证（专为外部系统设计）")
    print("- 自动验证关联数据的有效性")
    print("- 完整的错误处理和日志记录")
    
    print("\n📝 请求头:")
    print("Content-Type: application/json")
    
    print("\n📋 请求体参数:")
    print("- category_id (必填): 疾病分类ID (需存在且is_use=True)")
    print("- user_id (必填): 医生用户ID (需存在于user_doctor表)") 
    print("- hospital (可选): 医院名称")
    print("- phone (可选): 手机号")
    print("- level_id (可选): 劳务费档位ID (需存在于agreement_laborfee_level表)")
    print("- state_id (可选): 状态ID (需存在于works_worksstate表)")
    print("- payment_time (可选): 支付时间 (ISO格式: 2024-08-20T10:00:00Z)")
    print("- payment_amount (可选): 支付金额 (默认0.00)")
    print("- data (必填): 提交的答题数据 (JSON数组格式)")
    
    print("\n✅ 成功响应示例:")
    print("""{
    "code": 200,
    "msg": "提交成功",
    "data": {
        "id": 123,
        "created_at": "2024-08-20T10:30:00Z"
    }
}""")
    
    print("\n❌ 错误响应示例:")
    print("""{
    "code": 400,
    "msg": "提交失败: 疾病分类不存在或未启用",
    "data": []
}""")
    
    print("\n⚠️  注意事项:")
    print("1. 确保数据库中存在对应的category_id和user_id")
    print("2. data字段为JSON数组，包含题目和选项信息")
    print("3. 所有可选字段可以传null或不传")
    print("4. API会自动验证所有关联数据的有效性")
    print("=" * 80)

if __name__ == "__main__":
    print_api_documentation()
    print("\n开始API测试...")
    test_commitlog_api()
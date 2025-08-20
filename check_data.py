#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中的疾病分类和用户数据
运行前请确保激活了Django的虚拟环境
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RongChangE.settings')
sys.path.append('/Users/darren/project/RongChangE')
django.setup()

from survey.models import DiseasesCategory
from user.models import Doctor

def check_categories():
    """检查疾病分类数据"""
    print('=' * 50)
    print('疾病分类数据 (survey_diseasescategory)')
    print('=' * 50)
    
    categories = DiseasesCategory.objects.all().order_by('id')
    if not categories.exists():
        print("⚠️  没有找到疾病分类数据")
        return None
    
    for cat in categories:
        status = "✅ 启用" if cat.is_use else "❌ 未启用"
        print(f"ID: {cat.id:2d} | 标题: {cat.title:<15} | 状态: {status}")
    
    # 返回第一个启用的分类ID
    enabled_cat = categories.filter(is_use=True).first()
    return enabled_cat.id if enabled_cat else None

def check_doctors():
    """检查医生用户数据"""
    print('\n' + '=' * 50)
    print('医生用户数据 (user_doctor)')
    print('=' * 50)
    
    doctors = Doctor.objects.all().order_by('id')[:10]  # 只显示前10个
    if not doctors.exists():
        print("⚠️  没有找到医生用户数据")
        return None
    
    for doc in doctors:
        name = getattr(doc, 'name', '未设置')
        phone = getattr(doc, 'phone', '未设置') 
        print(f"ID: {doc.id:2d} | 姓名: {name:<10} | 手机: {phone}")
    
    # 返回第一个医生ID
    return doctors.first().id

def generate_test_data(category_id, user_id):
    """生成测试数据"""
    print('\n' + '=' * 50)
    print('推荐的测试数据')
    print('=' * 50)
    
    test_data = f'''{{
    "category_id": {category_id},
    "user_id": {user_id},
    "hospital": "测试医院",
    "phone": "13800138000",
    "level_id": null,
    "state_id": null,
    "payment_time": null,
    "payment_amount": 0.00,
    "data": [
        {{
            "id": 1,
            "title": "测试题目1",
            "scope": "测试范围",
            "kind": "S",
            "options": [
                {{
                    "id": 1,
                    "title": "选项A"
                }}
            ]
        }}
    ]
}}'''
    
    print("使用以下JSON数据测试API:")
    print(test_data)
    
    print(f"\n✅ curl测试命令:")
    print(f'curl -X POST http://127.0.0.1:8009/api/survey/external/commitlog/ \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f"  -d '{test_data.replace(chr(10), '')}'")

if __name__ == '__main__':
    try:
        category_id = check_categories()
        user_id = check_doctors()
        
        if category_id and user_id:
            generate_test_data(category_id, user_id)
        else:
            print("\n❌ 缺少必要的数据，请先在xadmin后台添加疾病分类和医生用户数据")
            
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        print("请确保:")
        print("1. Django虚拟环境已激活")
        print("2. 数据库连接正常")
        print("3. 相关模型和表已创建")
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试数据的脚本
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

def create_test_category():
    """创建测试用的疾病分类"""
    category, created = DiseasesCategory.objects.get_or_create(
        title="API测试分类",
        defaults={
            'order': 1,
            'is_use': True
        }
    )
    if created:
        print(f"✅ 创建疾病分类成功: ID={category.id}, 标题={category.title}")
    else:
        print(f"✅ 疾病分类已存在: ID={category.id}, 标题={category.title}")
    return category.id

def create_test_doctor():
    """创建测试用的医生用户"""
    try:
        # 尝试创建一个简单的医生记录
        doctor = Doctor.objects.create(
            name="API测试医生",
            phone="13800138000",
            state=2,  # 认证状态
            openid="test_openid_" + str(os.urandom(8).hex())
        )
        print(f"✅ 创建医生用户成功: ID={doctor.id}, 姓名={doctor.name}")
        return doctor.id
    except Exception as e:
        print(f"❌ 创建医生用户失败: {e}")
        # 如果创建失败，尝试找到现有的医生
        existing_doctor = Doctor.objects.first()
        if existing_doctor:
            print(f"✅ 使用现有医生: ID={existing_doctor.id}")
            return existing_doctor.id
        return None

def main():
    print("正在创建API测试所需的数据...")
    
    try:
        category_id = create_test_category()
        user_id = create_test_doctor()
        
        if category_id and user_id:
            print(f"\n🎯 测试数据创建完成!")
            print(f"📋 请使用以下ID进行API测试:")
            print(f"   - category_id: {category_id}")
            print(f"   - user_id: {user_id}")
            
            # 生成测试命令
            test_json = f'{{"category_id": {category_id}, "user_id": {user_id}, "hospital": "测试医院", "phone": "13800138000", "data": [{{"id": 1, "title": "测试题目", "scope": "测试", "kind": "S", "options": [{{"id": 1, "title": "选项A"}}]}}]}}'
            
            print(f"\n🚀 curl测试命令:")
            print(f"curl -X POST http://127.0.0.1:8009/api/survey/external/commitlog/ \\")
            print(f"  -H \"Content-Type: application/json\" \\")
            print(f"  -d '{test_json}'")
            
        else:
            print("❌ 创建测试数据失败")
            
    except Exception as e:
        print(f"❌ 执行出错: {e}")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
执行加替沙星眼用凝胶问卷数据插入脚本
"""
import os
import django
import sys

# 添加项目路径到 Python 路径
sys.path.append('./')

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RongChangE.settings')
django.setup()

from django.db import connection
from survey.models import DiseasesCategory, QuestionBank, Option

def insert_gatifloxacin_questionnaire():
    """插入加替沙星眼用凝胶临床观察问卷数据"""
    
    print("开始插入加替沙星眼用凝胶临床观察问卷数据...")
    
    # 1. 创建问卷分类
    category = DiseasesCategory.objects.create(
        title='加替沙星眼用凝胶临床观察',
        order=100,
        is_use=True
    )
    
    print(f"✓ 创建问卷分类: {category.title} (ID: {category.id})")
    
    # 2. 定义问题数据
    questions_data = [
        # 基本信息
        {'scope': '基本信息', 'kind': 'S', 'title': '患者性别', 'options': ['男', '女']},
        {'scope': '基本信息', 'kind': 'S', 'title': '是否进行手术', 'options': ['否', '是']},
        {'scope': '基本信息', 'kind': 'S', 'title': '研究眼别（如已手术）', 'options': ['右眼', '左眼']},
        {'scope': '基本信息', 'kind': 'T', 'title': '手术方式（如已手术）', 'options': ['手术方式描述']},
        
        # 首诊检查
        {'scope': '首诊检查', 'kind': 'S', 'title': '首诊结膜检查结果', 'options': ['正常', '异常']},
        {'scope': '首诊检查', 'kind': 'S', 'title': '首诊角膜检查结果', 'options': ['正常', '异常']},
        {'scope': '首诊检查', 'kind': 'S', 'title': '首诊前房检查结果', 'options': ['正常', '异常']},
        {'scope': '首诊检查', 'kind': 'S', 'title': '首诊玻璃体及眼底检查结果', 'options': ['正常', '异常']},
        {'scope': '首诊检查', 'kind': 'S', 'title': '既往是否使用眼部治疗药物', 'options': ['无', '有']},
        {'scope': '首诊检查', 'kind': 'S', 'title': '是否有药物过敏史', 'options': ['无', '有']},
        
        # 首诊感染指标评估
        {'scope': '首诊感染指标', 'kind': 'P', 'title': '首诊畏光程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '首诊感染指标', 'kind': 'P', 'title': '首诊异物感程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '首诊感染指标', 'kind': 'P', 'title': '首诊结膜充血程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '首诊感染指标', 'kind': 'P', 'title': '首诊分泌物程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        
        # 用药方案
        {'scope': '用药方案', 'kind': 'S', 'title': '加替沙星眼用凝胶每日使用次数', 'options': ['每日1次', '每日2次', '每日3次', '每日4次']},
        {'scope': '用药方案', 'kind': 'S', 'title': '是否合并使用其他眼部药物', 'options': ['无', '有']},
        
        # 复查检查
        {'scope': '复查检查', 'kind': 'S', 'title': '复查结膜检查结果', 'options': ['正常', '异常']},
        {'scope': '复查检查', 'kind': 'S', 'title': '复查角膜检查结果', 'options': ['正常', '异常']},
        {'scope': '复查检查', 'kind': 'S', 'title': '复查前房检查结果', 'options': ['正常', '异常']},
        {'scope': '复查检查', 'kind': 'S', 'title': '复查玻璃体及眼底检查结果', 'options': ['正常', '异常']},
        
        # 复查感染指标评估
        {'scope': '复查感染指标', 'kind': 'P', 'title': '复查畏光程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '复查感染指标', 'kind': 'P', 'title': '复查异物感程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '复查感染指标', 'kind': 'P', 'title': '复查结膜充血程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '复查感染指标', 'kind': 'P', 'title': '复查分泌物程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        
        # 疗效评估
        {'scope': '疗效评估', 'kind': 'S', 'title': '本次感染治疗效果判定', 'options': ['痊愈', '显效', '有效', '无效']},
        
        # 安全性评估
        {'scope': '安全性评估', 'kind': 'P', 'title': '眼部耐受性评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '安全性评估', 'kind': 'P', 'title': '烧灼感程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '安全性评估', 'kind': 'P', 'title': '眼刺痛程度评分（0-3分）', 'options': ['0分', '1分', '2分', '3分']},
        {'scope': '安全性评估', 'kind': 'S', 'title': '视力质量变化情况', 'options': ['视觉质量有提高', '视觉质量无改变']},
        
        # 不良反应评估
        {'scope': '不良反应', 'kind': 'S', 'title': '结膜刺激、流泪程度', 'options': ['无', '轻', '中', '重']},
        {'scope': '不良反应', 'kind': 'S', 'title': '角膜炎和乳头状结膜炎程度', 'options': ['无', '轻', '中', '重']},
        {'scope': '不良反应', 'kind': 'S', 'title': '是否有其他不良反应症状', 'options': ['无', '有']},
    ]
    
    # 3. 插入问题和选项
    total_questions = 0
    total_options = 0
    
    for question_data in questions_data:
        # 创建问题
        question = QuestionBank.objects.create(
            category=category,
            scope=question_data['scope'],
            kind=question_data['kind'],
            title=question_data['title'],
            is_use=True
        )
        total_questions += 1
        
        # 创建选项
        for idx, option_title in enumerate(question_data['options']):
            Option.objects.create(
                question=question,
                title=option_title,
                order=len(question_data['options']) - idx - 1  # 倒序排列
            )
            total_options += 1
        
        print(f"✓ 创建问题: {question.title} ({len(question_data['options'])} 个选项)")
    
    print(f"\n数据插入完成!")
    print(f"- 问卷分类ID: {category.id}")
    print(f"- 插入问题数量: {total_questions}")
    print(f"- 插入选项数量: {total_options}")
    
    # 验证数据
    print(f"\n验证数据:")
    print(f"- 分类标题: {category.title}")
    print(f"- 分类状态: {'启用' if category.is_use else '禁用'}")
    
    questions = QuestionBank.objects.filter(category=category)
    print(f"- 问题数量: {questions.count()}")
    
    for question in questions[:5]:  # 显示前5个问题
        options_count = Option.objects.filter(question=question).count()
        print(f"  * {question.title} ({question.kind}) - {options_count} 个选项")
    
    if questions.count() > 5:
        print(f"  ... 还有 {questions.count() - 5} 个问题")
    
    return category.id

def test_api_with_new_category(category_id):
    """测试新创建的问卷分类接口"""
    import requests
    
    print(f"\n开始测试接口...")
    
    url = f"http://localhost:8009/api/survey/questionnaire-detail/{category_id}/"
    headers = {
        'openid': 'oMTC06hC3OREwUQ6XSOhgDA2iooo',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                questionnaire = data['data']
                category_info = questionnaire.get('category', {})
                questions = questionnaire.get('questions', [])
                
                print(f"✓ 接口调用成功!")
                print(f"- 问卷分类: {category_info.get('title')}")
                print(f"- 问题数量: {len(questions)}")
                
                # 检查是否所有问题都有选项
                questions_without_options = [q for q in questions if not q.get('options')]
                if questions_without_options:
                    print(f"✗ 发现 {len(questions_without_options)} 个问题没有选项:")
                    for q in questions_without_options:
                        print(f"  - {q.get('title')}")
                else:
                    print(f"✓ 所有问题都有选项数据")
                    
                # 显示问题类型分布
                type_counts = {}
                for q in questions:
                    kind = q.get('kind')
                    type_counts[kind] = type_counts.get(kind, 0) + 1
                
                print(f"- 问题类型分布:")
                for kind, count in type_counts.items():
                    kind_name = {'S': '单选题', 'D': '多选题', 'P': '评分题', 'T': '排序题'}.get(kind, kind)
                    print(f"  * {kind_name}: {count} 题")
                    
            else:
                print(f"✗ 接口返回错误: {data}")
        else:
            print(f"✗ 接口调用失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ 连接失败 - 请确保服务器正在运行")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

if __name__ == "__main__":
    try:
        category_id = insert_gatifloxacin_questionnaire()
        test_api_with_new_category(category_id)
    except Exception as e:
        print(f"执行失败: {e}")
        import traceback
        traceback.print_exc()
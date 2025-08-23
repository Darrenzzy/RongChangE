#!/usr/bin/env python3
"""
直接连接数据库插入加替沙星眼用凝胶问卷数据
"""
import mysql.connector
from datetime import datetime
import sys

# 数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'user1',
    'password': 'password',
    'database': 'app',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"数据库连接失败: {e}")
        return None

def insert_category(cursor):
    """插入问卷分类"""
    print("1. 插入问卷分类...")
    
    # 检查是否已存在
    check_sql = "SELECT id FROM survey_diseasescategory WHERE title = %s"
    cursor.execute(check_sql, ('加替沙星眼用凝胶临床观察',))
    existing = cursor.fetchone()
    
    if existing:
        category_id = existing[0]
        print(f"   分类已存在，ID: {category_id}")
        return category_id
    
    # 插入新分类
    insert_sql = """
    INSERT INTO survey_diseasescategory (title, `order`, is_use, created_at, updated_at) 
    VALUES (%s, %s, %s, %s, %s)
    """
    now = datetime.now()
    cursor.execute(insert_sql, ('加替沙星眼用凝胶临床观察', 100, 1, now, now))
    category_id = cursor.lastrowid
    print(f"   ✓ 分类插入成功，ID: {category_id}")
    return category_id

def insert_questions(cursor, category_id):
    """插入问题数据"""
    print("2. 插入问题数据...")
    
    questions_data = [
        # 基本信息
        ('基本信息', 'S', '患者性别'),
        ('基本信息', 'S', '是否进行手术'),
        ('基本信息', 'S', '研究眼别（如已手术）'),
        ('基本信息', 'T', '手术方式（如已手术）'),
        
        # 首诊检查
        ('首诊检查', 'S', '首诊结膜检查结果'),
        ('首诊检查', 'S', '首诊角膜检查结果'),
        ('首诊检查', 'S', '首诊前房检查结果'),
        ('首诊检查', 'S', '首诊玻璃体及眼底检查结果'),
        ('首诊检查', 'S', '既往是否使用眼部治疗药物'),
        ('首诊检查', 'S', '是否有药物过敏史'),
        
        # 首诊感染指标评估
        ('首诊感染指标', 'P', '首诊畏光程度评分（0-3分）'),
        ('首诊感染指标', 'P', '首诊异物感程度评分（0-3分）'),
        ('首诊感染指标', 'P', '首诊结膜充血程度评分（0-3分）'),
        ('首诊感染指标', 'P', '首诊分泌物程度评分（0-3分）'),
        
        # 用药方案
        ('用药方案', 'S', '加替沙星眼用凝胶每日使用次数'),
        ('用药方案', 'S', '是否合并使用其他眼部药物'),
        
        # 复查检查
        ('复查检查', 'S', '复查结膜检查结果'),
        ('复查检查', 'S', '复查角膜检查结果'),
        ('复查检查', 'S', '复查前房检查结果'),
        ('复查检查', 'S', '复查玻璃体及眼底检查结果'),
        
        # 复查感染指标评估
        ('复查感染指标', 'P', '复查畏光程度评分（0-3分）'),
        ('复查感染指标', 'P', '复查异物感程度评分（0-3分）'),
        ('复查感染指标', 'P', '复查结膜充血程度评分（0-3分）'),
        ('复查感染指标', 'P', '复查分泌物程度评分（0-3分）'),
        
        # 疗效评估
        ('疗效评估', 'S', '本次感染治疗效果判定'),
        
        # 安全性评估
        ('安全性评估', 'P', '眼部耐受性评分（0-3分）'),
        ('安全性评估', 'P', '烧灼感程度评分（0-3分）'),
        ('安全性评估', 'P', '眼刺痛程度评分（0-3分）'),
        ('安全性评估', 'S', '视力质量变化情况'),
        
        # 不良反应评估
        ('不良反应', 'S', '结膜刺激、流泪程度'),
        ('不良反应', 'S', '角膜炎和乳头状结膜炎程度'),
        ('不良反应', 'S', '是否有其他不良反应症状'),
    ]
    
    insert_sql = """
    INSERT INTO survey_questionbank (category_id, scope, kind, title, is_use, created_at, updated_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    question_ids = {}
    now = datetime.now()
    
    for scope, kind, title in questions_data:
        # 检查问题是否已存在
        check_sql = "SELECT id FROM survey_questionbank WHERE category_id = %s AND title = %s"
        cursor.execute(check_sql, (category_id, title))
        existing = cursor.fetchone()
        
        if existing:
            question_id = existing[0]
            print(f"   问题已存在: {title} (ID: {question_id})")
        else:
            cursor.execute(insert_sql, (category_id, scope, kind, title, 1, now, now))
            question_id = cursor.lastrowid
            print(f"   ✓ 插入问题: {title} (ID: {question_id})")
        
        question_ids[title] = question_id
    
    print(f"   总计插入 {len(questions_data)} 个问题")
    return question_ids

def insert_options(cursor, question_ids):
    """插入选项数据"""
    print("3. 插入选项数据...")
    
    # 定义选项数据
    options_data = {
        '患者性别': ['男', '女'],
        '是否进行手术': ['否', '是'],
        '研究眼别（如已手术）': ['右眼', '左眼'],
        '手术方式（如已手术）': ['手术方式描述'],
        
        # 检查结果 - 正常/异常
        '首诊结膜检查结果': ['正常', '异常'],
        '首诊角膜检查结果': ['正常', '异常'],
        '首诊前房检查结果': ['正常', '异常'],
        '首诊玻璃体及眼底检查结果': ['正常', '异常'],
        '复查结膜检查结果': ['正常', '异常'],
        '复查角膜检查结果': ['正常', '异常'],
        '复查前房检查结果': ['正常', '异常'],
        '复查玻璃体及眼底检查结果': ['正常', '异常'],
        
        # 是否问题 - 无/有
        '既往是否使用眼部治疗药物': ['无', '有'],
        '是否有药物过敏史': ['无', '有'],
        '是否合并使用其他眼部药物': ['无', '有'],
        '是否有其他不良反应症状': ['无', '有'],
        
        # 评分题 - 0-3分
        '首诊畏光程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '首诊异物感程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '首诊结膜充血程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '首诊分泌物程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '复查畏光程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '复查异物感程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '复查结膜充血程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '复查分泌物程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '眼部耐受性评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '烧灼感程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        '眼刺痛程度评分（0-3分）': ['0分', '1分', '2分', '3分'],
        
        # 用药频次
        '加替沙星眼用凝胶每日使用次数': ['每日1次', '每日2次', '每日3次', '每日4次'],
        
        # 疗效判定
        '本次感染治疗效果判定': ['痊愈', '显效', '有效', '无效'],
        
        # 视力变化
        '视力质量变化情况': ['视觉质量有提高', '视觉质量无改变'],
        
        # 不良反应程度
        '结膜刺激、流泪程度': ['无', '轻', '中', '重'],
        '角膜炎和乳头状结膜炎程度': ['无', '轻', '中', '重'],
    }
    
    insert_sql = """
    INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) 
    VALUES (%s, %s, %s, %s, %s)
    """
    
    total_options = 0
    now = datetime.now()
    
    for question_title, options in options_data.items():
        if question_title not in question_ids:
            print(f"   ⚠️  警告: 未找到问题 '{question_title}'")
            continue
            
        question_id = question_ids[question_title]
        
        # 检查选项是否已存在
        check_sql = "SELECT COUNT(*) FROM survey_option WHERE question_id = %s"
        cursor.execute(check_sql, (question_id,))
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"   问题 '{question_title}' 已有 {existing_count} 个选项")
            continue
        
        # 插入选项（倒序排列）
        for idx, option_title in enumerate(options):
            order = len(options) - idx - 1
            cursor.execute(insert_sql, (question_id, option_title, order, now, now))
            total_options += 1
        
        print(f"   ✓ 为问题 '{question_title}' 插入 {len(options)} 个选项")
    
    print(f"   总计插入 {total_options} 个选项")

def verify_data(cursor, category_id):
    """验证数据完整性"""
    print("4. 验证数据完整性...")
    
    # 统计问题数量
    cursor.execute("SELECT COUNT(*) FROM survey_questionbank WHERE category_id = %s", (category_id,))
    question_count = cursor.fetchone()[0]
    
    # 统计选项数量
    cursor.execute("""
        SELECT COUNT(*) FROM survey_option o 
        JOIN survey_questionbank q ON o.question_id = q.id 
        WHERE q.category_id = %s
    """, (category_id,))
    option_count = cursor.fetchone()[0]
    
    # 检查没有选项的问题
    cursor.execute("""
        SELECT q.id, q.title, q.kind, COUNT(o.id) as option_count
        FROM survey_questionbank q 
        LEFT JOIN survey_option o ON q.id = o.question_id
        WHERE q.category_id = %s
        GROUP BY q.id, q.title, q.kind
        HAVING COUNT(o.id) = 0
    """, (category_id,))
    
    questions_without_options = cursor.fetchall()
    
    print(f"   - 问题数量: {question_count}")
    print(f"   - 选项数量: {option_count}")
    
    if questions_without_options:
        print(f"   ⚠️  发现 {len(questions_without_options)} 个问题没有选项:")
        for q_id, title, kind, opt_count in questions_without_options:
            print(f"     * ID: {q_id}, 标题: {title}, 类型: {kind}")
    else:
        print("   ✓ 所有问题都有选项")
    
    # 统计问题类型
    cursor.execute("""
        SELECT kind, COUNT(*) 
        FROM survey_questionbank 
        WHERE category_id = %s 
        GROUP BY kind
    """, (category_id,))
    
    type_stats = cursor.fetchall()
    print("   - 问题类型分布:")
    type_names = {'S': '单选题', 'D': '多选题', 'P': '评分题', 'T': '排序题'}
    for kind, count in type_stats:
        print(f"     * {type_names.get(kind, kind)}: {count} 题")
    
    return question_count, option_count, len(questions_without_options) == 0

def main():
    """主函数"""
    print("=" * 60)
    print("加替沙星眼用凝胶临床观察问卷数据插入")
    print("=" * 60)
    
    # 连接数据库
    connection = get_db_connection()
    if not connection:
        print("数据库连接失败，退出程序")
        return False
    
    try:
        cursor = connection.cursor()
        
        # 执行插入操作
        category_id = insert_category(cursor)
        question_ids = insert_questions(cursor, category_id)
        insert_options(cursor, question_ids)
        
        # 提交事务
        connection.commit()
        print("\n✓ 数据提交成功")
        
        # 验证数据
        print()
        question_count, option_count, all_complete = verify_data(cursor, category_id)
        
        print("\n" + "=" * 60)
        print("插入完成！")
        print(f"- 问卷分类ID: {category_id}")
        print(f"- 问题数量: {question_count}")
        print(f"- 选项数量: {option_count}")
        print(f"- 数据完整性: {'✓ 完整' if all_complete else '⚠️  有缺失'}")
        print("=" * 60)
        
        # 提供测试命令
        print("\n测试接口命令:")
        print(f"curl -X GET \"http://localhost:8009/api/survey/questionnaire-detail/{category_id}/\" \\")
        print('  -H "openid: oMTC06hC3OREwUQ6XSOhgDA2iooo" \\')
        print('  -H "Content-Type: application/json"')
        
        return True
        
    except mysql.connector.Error as e:
        print(f"\n❌ 数据库操作失败: {e}")
        connection.rollback()
        return False
        
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
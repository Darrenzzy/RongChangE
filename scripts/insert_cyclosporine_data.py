#!/usr/bin/env python3
"""
直接连接数据库插入0.05%环孢素滴眼液问卷数据
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
    cursor.execute(check_sql, ('0.05%环孢素滴眼液（II）临床观察',))
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
    cursor.execute(insert_sql, ('0.05%环孢素滴眼液（II）临床观察', 98, 1, now, now))
    category_id = cursor.lastrowid
    print(f"   ✓ 分类插入成功，ID: {category_id}")
    return category_id

def insert_questions(cursor, category_id):
    """插入问题数据"""
    print("2. 插入问题数据...")
    
    questions_data = [
        # 基本信息
        ('基本信息', 'T', '患者姓名'),
        ('基本信息', 'S', '患者性别'),
        ('基本信息', 'T', '患者年龄'),
        ('基本信息', 'T', '诊断结果'),
        ('基本信息', 'T', '干眼严重程度'),
        ('基本信息', 'T', '基础疾病'),
        
        # 首诊用药信息
        ('首诊用药信息', 'S', '兹润每天使用次数'),
        ('首诊用药信息', 'T', '处方单上传说明'),
        ('首诊用药信息', 'S', '是否合并用药'),
        ('首诊用药信息', 'T', '合并用药方案-药物1通用名'),
        ('首诊用药信息', 'T', '合并用药方案-药物1点眼频次'),
        ('首诊用药信息', 'T', '合并用药方案-药物2通用名'),
        ('首诊用药信息', 'T', '合并用药方案-药物2点眼频次'),
        ('首诊用药信息', 'T', '合并用药方案-药物3通用名'),
        ('首诊用药信息', 'T', '合并用药方案-药物3点眼频次'),
        ('首诊用药信息', 'T', '合并用药方案-药物4通用名'),
        ('首诊用药信息', 'T', '合并用药方案-药物4点眼频次'),
        
        # 首诊症状评价
        ('首诊症状评价', 'P', '首诊OSDI评分'),
        
        # 首诊体征评价
        ('首诊体征评价', 'P', '首诊结膜充血评分-右眼（0-4分）'),
        ('首诊体征评价', 'P', '首诊结膜充血评分-左眼（0-4分）'),
        ('首诊体征评价', 'P', '首诊角膜荧光染色评分-右眼（0-4分）'),
        ('首诊体征评价', 'P', '首诊角膜荧光染色评分-左眼（0-4分）'),
        ('首诊体征评价', 'T', '首诊BUT数值-右眼（秒）'),
        ('首诊体征评价', 'T', '首诊BUT数值-左眼（秒）'),
        ('首诊体征评价', 'T', '首诊Schirmer数值-右眼（mm/5min）'),
        ('首诊体征评价', 'T', '首诊Schirmer数值-左眼（mm/5min）'),
        ('首诊体征评价', 'T', '首诊泪河高度数值-右眼'),
        ('首诊体征评价', 'T', '首诊泪河高度数值-左眼'),
        ('首诊体征评价', 'P', '首诊睑板腺分泌物性状评分-右眼（0-4分）'),
        ('首诊体征评价', 'P', '首诊睑板腺分泌物性状评分-左眼（0-4分）'),
        ('首诊体征评价', 'P', '首诊睑板腺排出能力评分-右眼（0-4分）'),
        ('首诊体征评价', 'P', '首诊睑板腺排出能力评分-左眼（0-4分）'),
        ('首诊体征评价', 'T', '首诊脂质层厚度-右眼'),
        ('首诊体征评价', 'T', '首诊脂质层厚度-左眼'),
        ('首诊体征评价', 'T', '首诊检查照片上传说明'),
        
        # 1个月随访症状评价
        ('1个月随访症状评价', 'P', '1个月随访OSDI评分'),
        
        # 1个月随访体征评价
        ('1个月随访体征评价', 'P', '随访结膜充血评分-右眼（0-4分）'),
        ('1个月随访体征评价', 'P', '随访结膜充血评分-左眼（0-4分）'),
        ('1个月随访体征评价', 'P', '随访角膜荧光染色评分-右眼（0-4分）'),
        ('1个月随访体征评价', 'P', '随访角膜荧光染色评分-左眼（0-4分）'),
        ('1个月随访体征评价', 'T', '随访BUT数值-右眼（秒）'),
        ('1个月随访体征评价', 'T', '随访BUT数值-左眼（秒）'),
        ('1个月随访体征评价', 'T', '随访Schirmer数值-右眼（mm/5min）'),
        ('1个月随访体征评价', 'T', '随访Schirmer数值-左眼（mm/5min）'),
        ('1个月随访体征评价', 'T', '随访泪河高度数值-右眼'),
        ('1个月随访体征评价', 'T', '随访泪河高度数值-左眼'),
        ('1个月随访体征评价', 'P', '随访睑板腺分泌物性状评分-右眼（0-4分）'),
        ('1个月随访体征评价', 'P', '随访睑板腺分泌物性状评分-左眼（0-4分）'),
        ('1个月随访体征评价', 'P', '随访睑板腺排出能力评分-右眼（0-4分）'),
        ('1个月随访体征评价', 'P', '随访睑板腺排出能力评分-左眼（0-4分）'),
        ('1个月随访体征评价', 'T', '随访脂质层厚度-右眼'),
        ('1个月随访体征评价', 'T', '随访脂质层厚度-左眼'),
        ('1个月随访体征评价', 'T', '随访检查照片上传说明'),
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
        # 基本信息
        '患者姓名': ['请输入患者姓名'],
        '患者性别': ['男', '女'],
        '患者年龄': ['请输入患者年龄'],
        '诊断结果': ['请输入诊断结果'],
        '干眼严重程度': ['请输入干眼严重程度'],
        '基础疾病': ['请输入基础疾病'],
        
        # 首诊用药信息
        '兹润每天使用次数': ['每天1次', '每天2次', '每天3次', '每天4次'],
        '处方单上传说明': ['请上传处方单'],
        '是否合并用药': ['无', '有'],
        '合并用药方案-药物1通用名': ['请输入药物1通用名'],
        '合并用药方案-药物1点眼频次': ['请输入药物1点眼频次'],
        '合并用药方案-药物2通用名': ['请输入药物2通用名'],
        '合并用药方案-药物2点眼频次': ['请输入药物2点眼频次'],
        '合并用药方案-药物3通用名': ['请输入药物3通用名'],
        '合并用药方案-药物3点眼频次': ['请输入药物3点眼频次'],
        '合并用药方案-药物4通用名': ['请输入药物4通用名'],
        '合并用药方案-药物4点眼频次': ['请输入药物4点眼频次'],
        
        # OSDI评分（通常0-100分，可以按区间设置）
        '首诊OSDI评分': ['0-12分（正常）', '13-22分（轻度）', '23-32分（中度）', '33-100分（重度）', '具体分值'],
        '1个月随访OSDI评分': ['0-12分（正常）', '13-22分（轻度）', '23-32分（中度）', '33-100分（重度）', '具体分值'],
        
        # 体征评分（0-4分）- 首诊
        '首诊结膜充血评分-右眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '首诊结膜充血评分-左眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '首诊角膜荧光染色评分-右眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '首诊角膜荧光染色评分-左眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '首诊睑板腺分泌物性状评分-右眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '首诊睑板腺分泌物性状评分-左眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '首诊睑板腺排出能力评分-右眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '首诊睑板腺排出能力评分-左眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        
        # 体征评分（0-4分）- 随访
        '随访结膜充血评分-右眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '随访结膜充血评分-左眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '随访角膜荧光染色评分-右眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '随访角膜荧光染色评分-左眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '随访睑板腺分泌物性状评分-右眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '随访睑板腺分泌物性状评分-左眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '随访睑板腺排出能力评分-右眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        '随访睑板腺排出能力评分-左眼（0-4分）': ['0分', '1分', '2分', '3分', '4分'],
        
        # 数值测量（填空题）- 首诊
        '首诊BUT数值-右眼（秒）': ['请输入BUT数值（秒）'],
        '首诊BUT数值-左眼（秒）': ['请输入BUT数值（秒）'],
        '首诊Schirmer数值-右眼（mm/5min）': ['请输入Schirmer数值（mm/5min）'],
        '首诊Schirmer数值-左眼（mm/5min）': ['请输入Schirmer数值（mm/5min）'],
        '首诊泪河高度数值-右眼': ['请输入泪河高度数值'],
        '首诊泪河高度数值-左眼': ['请输入泪河高度数值'],
        '首诊脂质层厚度-右眼': ['请输入脂质层厚度'],
        '首诊脂质层厚度-左眼': ['请输入脂质层厚度'],
        '首诊检查照片上传说明': ['请上传检查照片'],
        
        # 数值测量（填空题）- 随访
        '随访BUT数值-右眼（秒）': ['请输入BUT数值（秒）'],
        '随访BUT数值-左眼（秒）': ['请输入BUT数值（秒）'],
        '随访Schirmer数值-右眼（mm/5min）': ['请输入Schirmer数值（mm/5min）'],
        '随访Schirmer数值-左眼（mm/5min）': ['请输入Schirmer数值（mm/5min）'],
        '随访泪河高度数值-右眼': ['请输入泪河高度数值'],
        '随访泪河高度数值-左眼': ['请输入泪河高度数值'],
        '随访脂质层厚度-右眼': ['请输入脂质层厚度'],
        '随访脂质层厚度-左眼': ['请输入脂质层厚度'],
        '随访检查照片上传说明': ['请上传检查照片'],
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
    
    # 统计调研范围
    cursor.execute("""
        SELECT scope, COUNT(*) 
        FROM survey_questionbank 
        WHERE category_id = %s 
        GROUP BY scope
        ORDER BY scope
    """, (category_id,))
    
    scope_stats = cursor.fetchall()
    print("   - 调研范围分布:")
    for scope, count in scope_stats:
        print(f"     * {scope}: {count} 题")
    
    return question_count, option_count, len(questions_without_options) == 0

def main():
    """主函数"""
    print("=" * 70)
    print("0.05%环孢素滴眼液（II）临床观察问卷数据插入")
    print("=" * 70)
    
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
        
        print("\n" + "=" * 70)
        print("插入完成！")
        print(f"- 问卷分类ID: {category_id}")
        print(f"- 问题数量: {question_count}")
        print(f"- 选项数量: {option_count}")
        print(f"- 数据完整性: {'✓ 完整' if all_complete else '⚠️  有缺失'}")
        print("=" * 70)
        
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
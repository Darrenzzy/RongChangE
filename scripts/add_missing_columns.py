#!/usr/bin/env python3
"""
手动添加缺失的数据库字段
"""
import mysql.connector
from mysql.connector import Error

def add_missing_columns():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            database='app',
            user='user1',
            password='password'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔧 开始添加缺失的字段...")
            
            # 添加gender字段
            try:
                cursor.execute("""
                    ALTER TABLE user_doctor 
                    ADD COLUMN gender varchar(10) NULL 
                    COMMENT '性别' AFTER name
                """)
                print("✅ 已添加 gender 字段")
            except Error as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  gender 字段已存在")
                else:
                    raise e
            
            # 添加birthday字段
            try:
                cursor.execute("""
                    ALTER TABLE user_doctor 
                    ADD COLUMN birthday date NULL 
                    COMMENT '出生日期' AFTER gender
                """)
                print("✅ 已添加 birthday 字段")
            except Error as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  birthday 字段已存在")
                else:
                    raise e
            
            connection.commit()
            print("🎉 字段添加完成!")
            
            # 再次查看表结构确认
            cursor.execute("DESCRIBE user_doctor")
            columns = cursor.fetchall()
            
            print("\n📋 更新后的表结构:")
            print("-" * 60)
            for column in columns:
                field, type_info, null, key, default, extra = column
                if field in ['gender', 'birthday']:
                    print(f"🆕 {field:18} {type_info:18} {null:8} {default or '无'}")
                    
    except Error as e:
        print(f"❌ 数据库错误: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_missing_columns()
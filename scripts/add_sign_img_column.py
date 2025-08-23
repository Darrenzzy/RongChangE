#!/usr/bin/env python3
"""
添加 sign_img 字段到数据库
"""
import mysql.connector
from mysql.connector import Error

def add_sign_img_column():
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
            
            print("🔧 开始添加 sign_img 字段...")
            
            # 添加 sign_img 字段
            try:
                cursor.execute("""
                    ALTER TABLE user_doctor 
                    ADD COLUMN sign_img TEXT NULL 
                    COMMENT '签名图片' AFTER pic
                """)
                print("✅ 已添加 sign_img 字段")
            except Error as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  sign_img 字段已存在")
                else:
                    raise e
            
            connection.commit()
            print("🎉 字段添加完成!")
            
            # 验证字段添加成功
            cursor.execute("DESCRIBE user_doctor")
            columns = cursor.fetchall()
            
            print("\n📋 验证新字段:")
            for column in columns:
                field, type_info, null, key, default, extra = column
                if field == 'sign_img':
                    print(f"🆕 {field:15} {type_info:15} {null:8} {default or '无'}")
                    break
            else:
                print("❌ sign_img 字段未找到")
                    
    except Error as e:
        print(f"❌ 数据库错误: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_sign_img_column()
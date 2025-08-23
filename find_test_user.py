#!/usr/bin/env python3
"""
查找可用于测试的医生记录（state=0）
"""
import mysql.connector
from mysql.connector import Error

def find_test_users():
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
            
            # 查询状态为0的医生记录
            cursor.execute("SELECT id, phone, name, openid, state, hospital FROM user_doctor WHERE state = 0")
            records = cursor.fetchall()
            
            print(f"📋 可用于测试的医生记录（state=0）:")
            print("-" * 80)
            print("ID | 手机号     | 姓名   | OpenID                    | 状态 | 医院")
            print("-" * 80)
            
            for record in records:
                id_val, phone, name, openid, state, hospital = record
                openid_display = (openid[:20] + "...") if openid and len(openid) > 20 else (openid or "无")
                print(f"{id_val:2} | {phone:10} | {name or '无':6} | {openid_display:25} | {state:4} | {hospital or '无'}")
                
    except Error as e:
        print(f"❌ 数据库错误: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    find_test_users()
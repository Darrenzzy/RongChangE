#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医生注册API测试脚本
用于测试 POST /api/user/doctor/ 接口

使用方法:
1. pip install requests  # 安装依赖
2. python3 doctor_api_demo.py
"""

import json
import time
import requests
from datetime import datetime

# API配置
API_BASE_URL = "http://127.0.0.1:8009"
CODE_API = "/api/user/code/"
DOCTOR_API = "/api/user/doctor/"

def send_verification_code(phone):
    """发送短信验证码"""
    url = f"{API_BASE_URL}{CODE_API}"
    data = {"phone": phone}
    
    print(f"📱 发送验证码到: {phone}")
    print(f"🔗 请求URL: {url}")
    print(f"📋 请求数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 0:
                print("✅ 验证码发送成功!")
                return True
            else:
                print(f"❌ 验证码发送失败: {result.get('msg')}")
                return False
        else:
            print("❌ 请求失败")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def create_doctor(phone, code, openid, pic):
    """医生注册"""
    url = f"{API_BASE_URL}{DOCTOR_API}"
    data = {
        "phone": phone,
        "code": code, 
        "openid": openid,
        "pic": pic
    }
    
    print(f"👨‍⚕️ 医生注册请求")
    print(f"🔗 请求URL: {url}")
    print(f"📋 请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 201:
            print("✅ 医生注册成功!")
            return True
        else:
            print(f"❌ 医生注册失败")
            if response.text:
                try:
                    error_info = response.json()
                    print(f"错误详情: {error_info}")
                except:
                    pass
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def print_api_documentation():
    """打印API使用文档"""
    print("=" * 80)
    print("医生注册API使用文档")
    print("=" * 80)
    
    print("\n🎯 API功能说明:")
    print("这不是创建新医生的API，而是医生注册激活API")
    print("- 将现有医生从'初始化'状态更新为'待审核'状态")
    print("- 绑定微信openid和医师执照")
    print("- 需要短信验证码验证身份")
    
    print("\n🔗 API端点:")
    print(f"验证码API: POST {API_BASE_URL}{CODE_API}")
    print(f"医生注册API: POST {API_BASE_URL}{DOCTOR_API}")
    
    print("\n📝 请求参数:")
    print("验证码API参数:")
    print("- phone (必填): 11位手机号")
    print("\n医生注册API参数:")
    print("- phone (必填): 11位手机号，必须在医生白名单中")
    print("- code (必填): 6位短信验证码")
    print("- openid (必填): 微信用户openid，不能重复")
    print("- pic (必填): 医师执照图片URL")
    
    print("\n📋 可用测试数据:")
    print("- 手机号: 32141 (状态: 初始化) ✅")
    print("- 手机号: 1111111 (状态: 初始化) ✅")
    print("- 手机号: 17766282334 (状态: 已认证) ❌")
    
    print("\n⚡ 使用流程:")
    print("1. 管理员在xladmin后台添加医生白名单")
    print("2. 调用验证码API发送短信")
    print("3. 获取验证码后调用医生注册API")
    print("4. 系统将医生状态更新为'待审核'")
    print("5. 管理员审核后状态变为'已认证'")
    
    print("=" * 80)

def interactive_test():
    """交互式测试"""
    print("\n🧪 交互式API测试")
    print("-" * 40)
    
    # 输入测试数据
    phone = input("请输入手机号 (建议: 32141): ").strip() or "32141"
    
    # 发送验证码
    if not send_verification_code(phone):
        print("验证码发送失败，测试终止")
        return
    
    # 等待用户输入验证码
    code = input("\n请输入收到的验证码 (6位数字): ").strip()
    if not code or len(code) != 6:
        print("验证码格式不正确，使用模拟验证码: 123456")
        code = "123456"
    
    # 生成测试数据
    timestamp = int(time.time())
    openid = f"test_openid_{timestamp}"
    pic = f"https://example.com/doctor_license_{timestamp}.jpg"
    
    print(f"\n生成的测试数据:")
    print(f"- openid: {openid}")
    print(f"- pic: {pic}")
    
    # 执行注册
    print("\n" + "=" * 50)
    create_doctor(phone, code, openid, pic)

def demo_test():
    """演示测试（不需要真实验证码）"""
    print("\n🎭 演示测试（模拟数据）")
    print("-" * 40)
    
    # 使用模拟数据
    phone = "32141"
    code = "123456"  # 模拟验证码
    openid = f"demo_openid_{int(time.time())}"
    pic = f"https://demo.com/license_{int(time.time())}.jpg"
    
    print("⚠️  注意：使用模拟验证码，API调用会失败，仅用于演示请求格式")
    
    # 先演示验证码API
    print("\n1. 演示验证码API调用:")
    send_verification_code(phone)
    
    # 再演示注册API
    print("\n2. 演示医生注册API调用:")
    create_doctor(phone, code, openid, pic)

def main():
    print_api_documentation()
    
    print("\n请选择测试模式:")
    print("1. 交互式测试 (需要真实验证码)")
    print("2. 演示测试 (使用模拟数据)")
    print("3. 只查看文档")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        interactive_test()
    elif choice == "2":
        demo_test()
    elif choice == "3":
        print("\n📚 文档已显示，测试结束")
    else:
        print("无效选择，使用演示模式")
        demo_test()

if __name__ == "__main__":
    main()
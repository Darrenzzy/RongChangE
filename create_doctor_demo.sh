#!/bin/bash

echo "=========================================="
echo "医生注册API测试脚本"
echo "=========================================="
echo "API路径: POST /api/user/doctor/"
echo "功能: 更新现有医生的openid和pic，状态改为待审核"
echo ""

# 配置
API_BASE_URL="http://127.0.0.1:8009"
DOCTOR_API="/api/user/doctor/"
CODE_API="/api/user/code/"

echo "1. 首先为测试手机号发送验证码..."

# 发送验证码（使用现有的初始化状态医生）
TEST_PHONE="32141"  # 使用现有的初始化状态医生手机号

echo "发送验证码给手机: $TEST_PHONE"
curl -X POST "${API_BASE_URL}${CODE_API}" \
  -H "Content-Type: application/json" \
  -d "{\"phone\": \"$TEST_PHONE\"}"

echo ""
echo ""
echo "⚠️  请查看短信验证码（或查看日志），然后输入验证码："
read -p "请输入收到的验证码: " VERIFICATION_CODE

echo ""
echo "2. 现在提交医生注册信息..."

# 医生注册API调用
curl -X POST "${API_BASE_URL}${DOCTOR_API}" \
  -H "Content-Type: application/json" \
  -d "{
    \"phone\": \"$TEST_PHONE\",
    \"code\": \"$VERIFICATION_CODE\",
    \"openid\": \"test_openid_$(date +%s)\",
    \"pic\": \"https://example.com/doctor_license_$(date +%s).jpg\"
  }"

echo ""
echo ""
echo "=========================================="
echo "API说明文档"
echo "=========================================="
echo ""
echo "🎯 API功能："
echo "- 这个API不是创建新医生，而是更新现有医生信息"
echo "- 将医生状态从'初始化'更新为'待审核'"
echo "- 绑定微信openid和上传医师执照pic"
echo ""
echo "📋 请求参数："
echo "- phone (必填): 手机号，必须是数据库中已存在的医生"
echo "- code (必填): 短信验证码，6位数字"
echo "- openid (必填): 微信用户openid"  
echo "- pic (必填): 医师执照图片URL"
echo ""
echo "🔄 业务逻辑："
echo "1. 验证短信验证码"
echo "2. 检查手机号是否在白名单（已存在的医生记录）"
echo "3. 检查openid是否已被使用"
echo "4. 更新医生的openid、pic字段"
echo "5. 将状态设置为'待审核'(state=1)"
echo ""
echo "✅ 成功响应: 201 Created"
echo "❌ 失败响应: 包含具体错误信息"
echo ""
echo "📱 前置条件："
echo "- 医生记录必须已存在于数据库（通过xadmin后台或Excel导入）"
echo "- 医生状态必须是'初始化'(state=0)"
echo "- 需要先调用验证码API获取短信验证码"
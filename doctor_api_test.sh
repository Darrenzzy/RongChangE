#!/bin/bash

echo "=========================================="
echo "医生注册API完整测试"
echo "=========================================="

API_BASE_URL="http://127.0.0.1:8009"

# 第一步：测试验证码发送API
echo "1. 测试验证码发送API"
echo "----------------------------"
echo "API: POST /api/user/code/"
echo "测试手机号: 32141 (现有初始化状态医生)"
echo ""

curl -X POST "$API_BASE_URL/api/user/code/" \
  -H "Content-Type: application/json" \
  -d '{"phone": "32141"}' \
  -w "\n\n"

echo "第二步：模拟医生注册（需要真实验证码）"
echo "----------------------------"
echo "API: POST /api/user/doctor/"
echo ""
echo "注意：实际使用时需要："
echo "1. 先调用验证码API"
echo "2. 获取真实的6位验证码"
echo "3. 替换下面请求中的code字段"
echo ""

# 示例请求（使用模拟验证码，实际会失败）
echo "示例请求JSON:"
cat << 'EOF'
{
  "phone": "32141",
  "code": "123456",
  "openid": "test_openid_20250820_001",
  "pic": "https://example.com/doctor_license_001.jpg"
}
EOF

echo ""
echo ""
echo "=========================================="
echo "完整的curl命令示例"
echo "=========================================="
echo ""
echo "# 1. 发送验证码"
echo "curl -X POST $API_BASE_URL/api/user/code/ \\"
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{"phone": "32141"}'\'''
echo ""
echo "# 2. 医生注册（替换real_code为真实验证码）"
echo "curl -X POST $API_BASE_URL/api/user/doctor/ \\"
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{'
echo '    "phone": "32141",'
echo '    "code": "real_code",'
echo '    "openid": "your_wechat_openid",'
echo '    "pic": "https://your-domain.com/doctor_license.jpg"'
echo '  }'\'''

echo ""
echo ""
echo "=========================================="
echo "API详细说明"
echo "=========================================="
echo ""
echo "🔗 API路径说明："
echo "- 验证码API: POST /api/user/code/"
echo "- 医生注册API: POST /api/user/doctor/"
echo "- 完整URL: $API_BASE_URL/api/user/doctor/"
echo ""
echo "📝 字段说明："
echo "- phone: 11位手机号，必须是数据库中已存在的医生"
echo "- code: 6位短信验证码，通过/api/user/code/获取"
echo "- openid: 微信用户唯一标识符"
echo "- pic: 医师执照图片URL地址"
echo ""
echo "⚡ 业务流程："
echo "1. 系统管理员通过xladmin后台添加医生到白名单"
echo "2. 医生通过微信小程序/公众号发起注册"
echo "3. 调用验证码API发送短信"
echo "4. 医生输入验证码、上传执照，调用注册API"
echo "5. 系统更新医生状态为'待审核'"
echo "6. 管理员审核通过后，状态变为'已认证'"
echo ""
echo "✅ 可用的测试数据："
echo "- 手机号: 32141 (状态: 初始化)"
echo "- 手机号: 1111111 (状态: 初始化)"
echo ""
echo "❌ 不可用的测试数据："
echo "- 手机号: 17766282334 (状态: 已认证)"
echo "- 手机号: 13087070314 (状态: 已认证)"
echo ""
echo "🔒 安全机制："
echo "- 手机号必须在白名单（预先存在的医生记录）"
echo "- openid不能重复使用"
echo "- 必须通过短信验证码验证"
echo "- 医师执照图片必须提供"
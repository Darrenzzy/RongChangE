# 问卷分类接口请求示例

## 接口信息
- **URL**: `GET /api/survey/category/`
- **认证方式**: HTTP 头部传递 `openid`
- **认证要求**: 用户必须存在且状态为已认证 (state=2)
- **响应格式**: JSON 数组，包含 id 和 title 字段

## 请求参数

### HTTP Headers (必需)
```
openid: oMTC06hC3OREwUQ6XSOhgDA2iooo
Content-Type: application/json
```

## 请求示例

### 1. curl 命令
```bash
curl -X GET "http://localhost:8000/api/survey/category/" \
  -H "openid: oMTC06hC3OREwUQ6XSOhgDA2iooo" \
  -H "Content-Type: application/json"
```

### 2. Python requests
```python
import requests

url = "http://localhost:8000/api/survey/category/"
headers = {
    'openid': 'oMTC06hC3OREwUQ6XSOhgDA2iooo',
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")
```

### 3. JavaScript fetch
```javascript
const response = await fetch('http://localhost:8000/api/survey/category/', {
    method: 'GET',
    headers: {
        'openid': 'oMTC06hC3OREwUQ6XSOhgDA2iooo',
        'Content-Type': 'application/json'
    }
});

const data = await response.json();
console.log('Status:', response.status);
console.log('Data:', data);
```

### 4. Postman 配置
```
Method: GET
URL: http://localhost:8000/api/survey/category/
Headers:
  openid: oMTC06hC3OREwUQ6XSOhgDA2iooo
  Content-Type: application/json
```

## 预期响应

### 成功响应 (200)
```json
[
    {
        "id": 1,
        "title": "类风湿性关节炎调研"
    },
    {
        "id": 2,
        "title": "糖尿病患者调研"
    }
]
```

### 认证失败 (400)
```json
{
    "detail": "请先完成认证哦"
}
```

## 认证说明

`RegisterDoctorAuthentication` 认证类要求：
1. HTTP 头部必须包含 `openid` 字段
2. 对应的医生用户必须存在
3. 医生用户的状态必须为 2（已认证）

如果认证失败，会返回 400 状态码和错误信息 "请先完成认证哦"。

## 注意事项

1. **openid 验证**: 提供的 openid `oMTC06hC3OREwUQ6XSOhgDA2iooo` 必须在数据库中存在且状态为已认证
2. **服务器地址**: 示例中使用 `localhost:8000`，实际使用时请替换为正确的服务器地址
3. **HTTPS**: 生产环境建议使用 HTTPS 协议
4. **错误处理**: 请妥善处理认证失败和网络错误的情况
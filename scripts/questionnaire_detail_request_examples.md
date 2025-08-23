# 问卷详情接口请求示例

## 接口信息
- **URL**: `GET /api/survey/questionnaire-detail/{category_id}/`
- **功能**: 获取指定问卷分类下的所有问题和选项
- **认证方式**: HTTP 头部传递 `openid`
- **认证要求**: 用户必须存在且状态为已认证 (state=2)

## 请求参数

### URL 参数
- `category_id`: 问卷分类ID (必需)

### HTTP Headers (必需)
```
openid: oMTC06hC3OREwUQ6XSOhgDA2iooo
Content-Type: application/json
```

## 请求示例

### 1. curl 命令
```bash
# 获取分类ID为17的问卷详情
curl -X GET "http://localhost:8000/api/survey/questionnaire-detail/17/" \
  -H "openid: oMTC06hC3OREwUQ6XSOhgDA2iooo" \
  -H "Content-Type: application/json"
```

### 2. Python requests
```python
import requests

category_id = 17
url = f"http://localhost:8000/api/survey/questionnaire-detail/{category_id}/"
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
const categoryId = 17;
const response = await fetch(`http://localhost:8000/api/survey/questionnaire-detail/${categoryId}/`, {
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
URL: http://localhost:8000/api/survey/questionnaire-detail/17/
Headers:
  openid: oMTC06hC3OREwUQ6XSOhgDA2iooo
  Content-Type: application/json
```

## 响应示例

### 成功响应 (200)
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "category": {
      "id": 17,
      "title": "类风湿性关节炎调研"
    },
    "questions": [
      {
        "id": 1,
        "title": "您诊治的患者中，缓解期患者占比是多少？",
        "scope": "患者的病程或疾病阶段",
        "kind": "S",
        "options": [
          {
            "id": 1,
            "title": "10%-20%",
            "order": 0
          },
          {
            "id": 2,
            "title": "21%-30%",
            "order": 0
          }
        ]
      },
      {
        "id": 2,
        "title": "您认为哪些因素会影响类风湿性关节炎的治疗费用？",
        "scope": "药物经济学",
        "kind": "D",
        "options": [
          {
            "id": 3,
            "title": "药物价格",
            "order": 0
          },
          {
            "id": 4,
            "title": "保险覆盖范围",
            "order": 0
          },
          {
            "id": 5,
            "title": "检查费用",
            "order": 0
          }
        ]
      }
    ]
  }
}
```

### 错误响应

#### 问卷分类不存在 (400)
```json
{
  "code": 400,
  "msg": "问卷分类不存在或未启用",
  "data": []
}
```

#### 问卷分类ID格式错误 (400)
```json
{
  "code": 400,
  "msg": "问卷分类ID格式错误",
  "data": []
}
```

#### 该问卷暂无题目 (400)
```json
{
  "code": 400,
  "msg": "该问卷暂无题目",
  "data": []
}
```

#### 认证失败 (400)
```json
{
  "detail": "请先完成认证哦"
}
```

## 数据字段说明

### 问题类型 (kind)
- `S`: 单选题
- `D`: 多选题  
- `P`: 评分题
- `T`: 排序题(填空题)

### 数据结构
- `category`: 问卷分类信息
  - `id`: 分类ID
  - `title`: 分类标题
- `questions`: 问题列表
  - `id`: 问题ID
  - `title`: 问题标题
  - `scope`: 调研范围
  - `kind`: 问题类型
  - `options`: 选项列表
    - `id`: 选项ID
    - `title`: 选项标题
    - `order`: 选项排序

## 使用场景

1. **完整问卷展示**: 获取问卷的所有问题用于完整展示
2. **问卷预览**: 在用户答题前预览问卷内容
3. **数据分析**: 获取问卷结构用于数据分析和报表
4. **问卷编辑**: 为问卷编辑功能提供数据源

## 注意事项

1. **认证要求**: 必须提供有效的已认证用户 openid
2. **过滤条件**: 只返回启用状态的问卷分类和问题 (is_use=True)
3. **数据完整性**: 包含问题的所有选项，按 order 字段排序
4. **错误处理**: 妥善处理不存在的分类ID和认证失败情况
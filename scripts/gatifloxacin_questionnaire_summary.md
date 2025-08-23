# 加替沙星眼用凝胶临床观察问卷数据总结

## 数据结构概览

### 问卷分类
- **标题**: 加替沙星眼用凝胶临床观察
- **状态**: 启用 (is_use=True)
- **排序**: 100

### 问题统计
- **总问题数**: 32题
- **问题类型分布**:
  - 单选题 (S): 23题
  - 评分题 (P): 8题
  - 排序题 (T): 1题

### 调研范围分类
1. **基本信息** (4题)
   - 患者性别
   - 是否进行手术
   - 研究眼别
   - 手术方式

2. **首诊检查** (6题)
   - 结膜、角膜、前房、玻璃体及眼底检查结果
   - 既往用药史和过敏史

3. **首诊感染指标** (4题)
   - 畏光、异物感、结膜充血、分泌物程度评分

4. **用药方案** (2题)
   - 用药频次和合并用药情况

5. **复查检查** (4题)
   - 复查时各项检查结果

6. **复查感染指标** (4题)
   - 复查时各项感染指标评分

7. **疗效评估** (1题)
   - 治疗效果判定

8. **安全性评估** (4题)
   - 耐受性、烧灼感、刺痛评分及视力变化

9. **不良反应** (3题)
   - 各类不良反应程度评估

## 题目类型说明

### 单选题 (S) - 23题
适用于二选一或多选一的情况，如：
- 性别选择（男/女）
- 检查结果（正常/异常）
- 是否情况（有/无）

### 评分题 (P) - 8题
用于程度评估，采用0-3分评分制：
- 0分：无症状
- 1分：轻度
- 2分：中度  
- 3分：重度

适用于主观症状评估，如畏光、异物感等。

### 排序题 (T) - 1题
用于开放性文本输入，如手术方式描述。

## 数据验证要点

### 选项完整性
- ✅ 每个问题都配置了相应选项
- ✅ 评分题统一采用0-3分制
- ✅ 单选题提供明确的选择项
- ✅ 排序题（填空题）提供输入提示

### 数据质量
- ✅ 问题标题清晰明确
- ✅ 调研范围分类合理
- ✅ 选项排序合理（order字段）
- ✅ 所有数据启用状态正确

## 接口测试

### 测试接口
```bash
curl -X GET "http://localhost:8009/api/survey/questionnaire-detail/{category_id}/" \
  -H "openid: oMTC06hC3OREwUQ6XSOhgDA2iooo" \
  -H "Content-Type: application/json"
```

### 预期结果
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "category": {
      "id": N,
      "title": "加替沙星眼用凝胶临床观察"
    },
    "questions": [
      {
        "id": N,
        "title": "问题标题",
        "scope": "调研范围",
        "kind": "S|P|T",
        "options": [
          {
            "id": N,
            "title": "选项标题",
            "order": N
          }
        ]
      }
    ]
  }
}
```

## 使用流程

1. **数据插入**
   ```bash
   python3 execute_gatifloxacin_insert.py
   ```

2. **获取分类ID**
   ```bash
   curl -X GET "http://localhost:8009/api/survey/category/" \
     -H "openid: oMTC06hC3OREwUQ6XSOhgDA2iooo"
   ```

3. **获取问卷详情**
   ```bash
   curl -X GET "http://localhost:8009/api/survey/questionnaire-detail/{category_id}/" \
     -H "openid: oMTC06hC3OREwUQ6XSOhgDA2iooo"
   ```

4. **验证结果**
   - 检查返回的问题数量（应为32题）
   - 确认每个问题都有选项数据
   - 验证问题类型分布正确

## 注意事项

1. **认证要求**: 所有接口都需要有效的 openid 认证
2. **数据完整性**: 确保插入数据后所有问题都有对应选项
3. **服务器端口**: 示例使用8009端口，请根据实际情况调整
4. **错误处理**: 如果接口返回空选项，请检查数据库中的关联关系

## 文件清单

- `gatifloxacin_questionnaire_insert.sql` - SQL插入脚本
- `execute_gatifloxacin_insert.py` - Python执行脚本
- `test_gatifloxacin_questionnaire.sh` - Shell测试脚本
- `gatifloxacin_questionnaire_summary.md` - 本总结文档
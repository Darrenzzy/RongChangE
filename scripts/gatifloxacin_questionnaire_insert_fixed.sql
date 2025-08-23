-- 加替沙星眼用凝胶临床观察病例表问卷数据插入脚本（修复版）

-- 1. 插入问卷分类
INSERT INTO survey_diseasescategory (title, `order`, is_use, created_at, updated_at) 
VALUES ('加替沙星眼用凝胶临床观察', 100, 1, NOW(), NOW());

-- 2. 插入问题数据（使用子查询获取分类ID）
INSERT INTO survey_questionbank (category_id, scope, kind, title, is_use, created_at, updated_at) VALUES 

-- 基本信息相关问题
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '基本信息', 'S', '患者性别', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '基本信息', 'S', '是否进行手术', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '基本信息', 'S', '研究眼别（如已手术）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '基本信息', 'T', '手术方式（如已手术）', 1, NOW(), NOW()),

-- 首诊检查相关问题
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊检查', 'S', '首诊结膜检查结果', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊检查', 'S', '首诊角膜检查结果', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊检查', 'S', '首诊前房检查结果', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊检查', 'S', '首诊玻璃体及眼底检查结果', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊检查', 'S', '既往是否使用眼部治疗药物', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊检查', 'S', '是否有药物过敏史', 1, NOW(), NOW()),

-- 首诊感染指标评估（评分题）
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊感染指标', 'P', '首诊畏光程度评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊感染指标', 'P', '首诊异物感程度评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊感染指标', 'P', '首诊结膜充血程度评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '首诊感染指标', 'P', '首诊分泌物程度评分（0-3分）', 1, NOW(), NOW()),

-- 用药方案相关
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '用药方案', 'S', '加替沙星眼用凝胶每日使用次数', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '用药方案', 'S', '是否合并使用其他眼部药物', 1, NOW(), NOW()),

-- 七天复查相关问题
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '复查检查', 'S', '复查结膜检查结果', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '复查检查', 'S', '复查角膜检查结果', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '复查检查', 'S', '复查前房检查结果', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '复查检查', 'S', '复查玻璃体及眼底检查结果', 1, NOW(), NOW()),

-- 复查感染指标评估（评分题）
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '复查感染指标', 'P', '复查畏光程度评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '复查感染指标', 'P', '复查异物感程度评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '复查感染指标', 'P', '复查结膜充血程度评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '复查感染指标', 'P', '复查分泌物程度评分（0-3分）', 1, NOW(), NOW()),

-- 疗效评估
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '疗效评估', 'S', '本次感染治疗效果判定', 1, NOW(), NOW()),

-- 安全性评估（评分题）
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '安全性评估', 'P', '眼部耐受性评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '安全性评估', 'P', '烧灼感程度评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '安全性评估', 'P', '眼刺痛程度评分（0-3分）', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '安全性评估', 'S', '视力质量变化情况', 1, NOW(), NOW()),

-- 药物不良反应评估
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '不良反应', 'S', '结膜刺激、流泪程度', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '不良反应', 'S', '角膜炎和乳头状结膜炎程度', 1, NOW(), NOW()),
((SELECT id FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1), '不良反应', 'S', '是否有其他不良反应症状', 1, NOW(), NOW());

-- 3. 插入选项数据
-- 患者性别选项
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) 
SELECT q.id, '男', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '患者性别'
UNION ALL
SELECT q.id, '女', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '患者性别'

UNION ALL

-- 是否手术选项
SELECT q.id, '否', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '是否进行手术'
UNION ALL
SELECT q.id, '是', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '是否进行手术'

UNION ALL

-- 研究眼别选项
SELECT q.id, '右眼', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '研究眼别（如已手术）'
UNION ALL
SELECT q.id, '左眼', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '研究眼别（如已手术）'

UNION ALL

-- 手术方式（填空题选项）
SELECT q.id, '手术方式描述', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '手术方式（如已手术）';

-- 为了简化，我们创建一个通用的插入脚本来处理重复的选项模式

-- 正常/异常选项（用于所有检查结果）
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '正常', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.title IN ('首诊结膜检查结果', '首诊角膜检查结果', '首诊前房检查结果', '首诊玻璃体及眼底检查结果',
                '复查结膜检查结果', '复查角膜检查结果', '复查前房检查结果', '复查玻璃体及眼底检查结果')
UNION ALL
SELECT q.id, '异常', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.title IN ('首诊结膜检查结果', '首诊角膜检查结果', '首诊前房检查结果', '首诊玻璃体及眼底检查结果',
                '复查结膜检查结果', '复查角膜检查结果', '复查前房检查结果', '复查玻璃体及眼底检查结果');

-- 无/有选项（用于既往用药史、过敏史等）
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '无', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.title IN ('既往是否使用眼部治疗药物', '是否有药物过敏史', '是否合并使用其他眼部药物', '是否有其他不良反应症状')
UNION ALL
SELECT q.id, '有', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.title IN ('既往是否使用眼部治疗药物', '是否有药物过敏史', '是否合并使用其他眼部药物', '是否有其他不良反应症状');

-- 评分题选项（0-3分）
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '0分', 3, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.kind = 'P'
UNION ALL
SELECT q.id, '1分', 2, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.kind = 'P'
UNION ALL
SELECT q.id, '2分', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.kind = 'P'
UNION ALL
SELECT q.id, '3分', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.kind = 'P';

-- 每日用药次数选项
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '每日1次', 3, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '加替沙星眼用凝胶每日使用次数'
UNION ALL
SELECT q.id, '每日2次', 2, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '加替沙星眼用凝胶每日使用次数'
UNION ALL
SELECT q.id, '每日3次', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '加替沙星眼用凝胶每日使用次数'
UNION ALL
SELECT q.id, '每日4次', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '加替沙星眼用凝胶每日使用次数';

-- 治疗效果判定选项
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '痊愈', 3, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '本次感染治疗效果判定'
UNION ALL
SELECT q.id, '显效', 2, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '本次感染治疗效果判定'
UNION ALL
SELECT q.id, '有效', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '本次感染治疗效果判定'
UNION ALL
SELECT q.id, '无效', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '本次感染治疗效果判定';

-- 视力质量变化选项
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '视觉质量有提高', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '视力质量变化情况'
UNION ALL
SELECT q.id, '视觉质量无改变', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' AND q.title = '视力质量变化情况';

-- 不良反应程度选项（无/轻/中/重）
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '无', 3, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.title IN ('结膜刺激、流泪程度', '角膜炎和乳头状结膜炎程度')
UNION ALL
SELECT q.id, '轻', 2, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.title IN ('结膜刺激、流泪程度', '角膜炎和乳头状结膜炎程度')
UNION ALL
SELECT q.id, '中', 1, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.title IN ('结膜刺激、流泪程度', '角膜炎和乳头状结膜炎程度')
UNION ALL
SELECT q.id, '重', 0, NOW(), NOW()
FROM survey_questionbank q 
JOIN survey_diseasescategory c ON q.category_id = c.id
WHERE c.title = '加替沙星眼用凝胶临床观察' 
AND q.title IN ('结膜刺激、流泪程度', '角膜炎和乳头状结膜炎程度');

-- 显示插入结果统计
SELECT 
    '插入完成' as '状态',
    c.id as '问卷分类ID',
    c.title as '问卷标题',
    (SELECT COUNT(*) FROM survey_questionbank WHERE category_id = c.id) as '问题数量',
    (SELECT COUNT(*) FROM survey_option o 
     JOIN survey_questionbank q ON o.question_id = q.id 
     WHERE q.category_id = c.id) as '选项数量'
FROM survey_diseasescategory c 
WHERE c.title = '加替沙星眼用凝胶临床观察'
ORDER BY c.id DESC 
LIMIT 1;
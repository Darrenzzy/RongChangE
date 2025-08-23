-- 加替沙星眼用凝胶临床观察问卷数据插入脚本（简化版）
-- 分步执行，避免MySQL变量问题

-- 步骤1: 插入问卷分类
INSERT INTO survey_diseasescategory (title, `order`, is_use, created_at, updated_at) 
VALUES ('加替沙星眼用凝胶临床观察', 100, 1, NOW(), NOW());

-- 步骤2: 查看插入的分类ID（请记录此ID用于后续步骤）
SELECT id, title FROM survey_diseasescategory WHERE title = '加替沙星眼用凝胶临床观察' ORDER BY id DESC LIMIT 1;

-- 步骤3: 插入问题数据
-- 请将下面的 {CATEGORY_ID} 替换为步骤2中获得的实际分类ID

-- 示例：如果分类ID是21，则替换所有的 {CATEGORY_ID} 为 21

INSERT INTO survey_questionbank (category_id, scope, kind, title, is_use, created_at, updated_at) VALUES 
-- 基本信息
({CATEGORY_ID}, '基本信息', 'S', '患者性别', 1, NOW(), NOW()),
({CATEGORY_ID}, '基本信息', 'S', '是否进行手术', 1, NOW(), NOW()),
({CATEGORY_ID}, '基本信息', 'S', '研究眼别（如已手术）', 1, NOW(), NOW()),
({CATEGORY_ID}, '基本信息', 'T', '手术方式（如已手术）', 1, NOW(), NOW()),

-- 首诊检查
({CATEGORY_ID}, '首诊检查', 'S', '首诊结膜检查结果', 1, NOW(), NOW()),
({CATEGORY_ID}, '首诊检查', 'S', '首诊角膜检查结果', 1, NOW(), NOW()),
({CATEGORY_ID}, '首诊检查', 'S', '首诊前房检查结果', 1, NOW(), NOW()),
({CATEGORY_ID}, '首诊检查', 'S', '首诊玻璃体及眼底检查结果', 1, NOW(), NOW()),
({CATEGORY_ID}, '首诊检查', 'S', '既往是否使用眼部治疗药物', 1, NOW(), NOW()),
({CATEGORY_ID}, '首诊检查', 'S', '是否有药物过敏史', 1, NOW(), NOW()),

-- 首诊感染指标
({CATEGORY_ID}, '首诊感染指标', 'P', '首诊畏光程度评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '首诊感染指标', 'P', '首诊异物感程度评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '首诊感染指标', 'P', '首诊结膜充血程度评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '首诊感染指标', 'P', '首诊分泌物程度评分（0-3分）', 1, NOW(), NOW()),

-- 用药方案
({CATEGORY_ID}, '用药方案', 'S', '加替沙星眼用凝胶每日使用次数', 1, NOW(), NOW()),
({CATEGORY_ID}, '用药方案', 'S', '是否合并使用其他眼部药物', 1, NOW(), NOW()),

-- 复查检查
({CATEGORY_ID}, '复查检查', 'S', '复查结膜检查结果', 1, NOW(), NOW()),
({CATEGORY_ID}, '复查检查', 'S', '复查角膜检查结果', 1, NOW(), NOW()),
({CATEGORY_ID}, '复查检查', 'S', '复查前房检查结果', 1, NOW(), NOW()),
({CATEGORY_ID}, '复查检查', 'S', '复查玻璃体及眼底检查结果', 1, NOW(), NOW()),

-- 复查感染指标
({CATEGORY_ID}, '复查感染指标', 'P', '复查畏光程度评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '复查感染指标', 'P', '复查异物感程度评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '复查感染指标', 'P', '复查结膜充血程度评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '复查感染指标', 'P', '复查分泌物程度评分（0-3分）', 1, NOW(), NOW()),

-- 疗效评估
({CATEGORY_ID}, '疗效评估', 'S', '本次感染治疗效果判定', 1, NOW(), NOW()),

-- 安全性评估
({CATEGORY_ID}, '安全性评估', 'P', '眼部耐受性评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '安全性评估', 'P', '烧灼感程度评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '安全性评估', 'P', '眼刺痛程度评分（0-3分）', 1, NOW(), NOW()),
({CATEGORY_ID}, '安全性评估', 'S', '视力质量变化情况', 1, NOW(), NOW()),

-- 不良反应
({CATEGORY_ID}, '不良反应', 'S', '结膜刺激、流泪程度', 1, NOW(), NOW()),
({CATEGORY_ID}, '不良反应', 'S', '角膜炎和乳头状结膜炎程度', 1, NOW(), NOW()),
({CATEGORY_ID}, '不良反应', 'S', '是否有其他不良反应症状', 1, NOW(), NOW());

-- 步骤4: 查看插入的问题（确认问题插入成功）
SELECT id, title, kind FROM survey_questionbank WHERE category_id = {CATEGORY_ID} ORDER BY id;

-- 步骤5: 插入选项数据
-- 同样需要替换 {CATEGORY_ID} 为实际的分类ID

-- 基本选项: 男/女
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) VALUES
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '患者性别'), '男', 1, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '患者性别'), '女', 0, NOW(), NOW());

-- 基本选项: 否/是
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) VALUES
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '是否进行手术'), '否', 1, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '是否进行手术'), '是', 0, NOW(), NOW());

-- 眼别选项: 右眼/左眼
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) VALUES
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '研究眼别（如已手术）'), '右眼', 1, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '研究眼别（如已手术）'), '左眼', 0, NOW(), NOW());

-- 手术方式（填空）
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) VALUES
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '手术方式（如已手术）'), '手术方式描述', 0, NOW(), NOW());

-- 批量插入：正常/异常选项（所有检查结果）
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '正常', 1, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID}
AND q.title LIKE '%检查结果'
UNION ALL
SELECT q.id, '异常', 0, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID}
AND q.title LIKE '%检查结果';

-- 批量插入：无/有选项
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '无', 1, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID}
AND (q.title LIKE '%是否%' OR q.title LIKE '%药物%' OR q.title = '是否有其他不良反应症状')
AND q.title NOT IN ('是否进行手术', '研究眼别（如已手术）')
UNION ALL
SELECT q.id, '有', 0, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID}
AND (q.title LIKE '%是否%' OR q.title LIKE '%药物%' OR q.title = '是否有其他不良反应症状')
AND q.title NOT IN ('是否进行手术', '研究眼别（如已手术）');

-- 批量插入：评分题选项（0-3分）
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '0分', 3, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID} AND q.kind = 'P'
UNION ALL
SELECT q.id, '1分', 2, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID} AND q.kind = 'P'
UNION ALL
SELECT q.id, '2分', 1, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID} AND q.kind = 'P'
UNION ALL
SELECT q.id, '3分', 0, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID} AND q.kind = 'P';

-- 用药次数选项
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) VALUES
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '加替沙星眼用凝胶每日使用次数'), '每日1次', 3, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '加替沙星眼用凝胶每日使用次数'), '每日2次', 2, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '加替沙星眼用凝胶每日使用次数'), '每日3次', 1, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '加替沙星眼用凝胶每日使用次数'), '每日4次', 0, NOW(), NOW());

-- 治疗效果选项
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) VALUES
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '本次感染治疗效果判定'), '痊愈', 3, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '本次感染治疗效果判定'), '显效', 2, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '本次感染治疗效果判定'), '有效', 1, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '本次感染治疗效果判定'), '无效', 0, NOW(), NOW());

-- 视力质量变化选项
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) VALUES
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '视力质量变化情况'), '视觉质量有提高', 1, NOW(), NOW()),
((SELECT id FROM survey_questionbank WHERE category_id = {CATEGORY_ID} AND title = '视力质量变化情况'), '视觉质量无改变', 0, NOW(), NOW());

-- 不良反应程度选项（无/轻/中/重）
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at)
SELECT q.id, '无', 3, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID}
AND q.title LIKE '%程度'
AND q.title NOT LIKE '%评分%'
UNION ALL
SELECT q.id, '轻', 2, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID}
AND q.title LIKE '%程度'
AND q.title NOT LIKE '%评分%'
UNION ALL
SELECT q.id, '中', 1, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID}
AND q.title LIKE '%程度'
AND q.title NOT LIKE '%评分%'
UNION ALL
SELECT q.id, '重', 0, NOW(), NOW()
FROM survey_questionbank q 
WHERE q.category_id = {CATEGORY_ID}
AND q.title LIKE '%程度'
AND q.title NOT LIKE '%评分%';

-- 步骤6: 验证数据完整性
SELECT 
    '数据统计' as '类型',
    COUNT(DISTINCT q.id) as '问题数量',
    COUNT(o.id) as '选项数量'
FROM survey_questionbank q 
LEFT JOIN survey_option o ON q.id = o.question_id
WHERE q.category_id = {CATEGORY_ID};

-- 检查没有选项的问题
SELECT 
    q.id,
    q.title,
    q.kind,
    COUNT(o.id) as option_count
FROM survey_questionbank q 
LEFT JOIN survey_option o ON q.id = o.question_id
WHERE q.category_id = {CATEGORY_ID}
GROUP BY q.id, q.title, q.kind
HAVING COUNT(o.id) = 0;
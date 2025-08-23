-- 加替沙星眼用凝胶临床观察病例表问卷数据插入脚本

-- 1. 插入问卷分类
INSERT INTO survey_diseasescategory (title, `order`, is_use, created_at, updated_at) 
VALUES ('加替沙星眼用凝胶临床观察', 100, 1, NOW(), NOW());

-- 获取刚插入的分类ID（假设为20，实际使用时需要查询）
SET @category_id = LAST_INSERT_ID();

-- 2. 插入问题数据

-- 基本信息相关问题
INSERT INTO survey_questionbank (category_id, scope, kind, title, is_use, created_at, updated_at) VALUES 
(@category_id, '基本信息', 'S', '患者性别', 1, NOW(), NOW()),
(@category_id, '基本信息', 'S', '是否进行手术', 1, NOW(), NOW()),
(@category_id, '基本信息', 'S', '研究眼别（如已手术）', 1, NOW(), NOW()),
(@category_id, '基本信息', 'T', '手术方式（如已手术）', 1, NOW(), NOW()),

-- 首诊检查相关问题
(@category_id, '首诊检查', 'S', '首诊结膜检查结果', 1, NOW(), NOW()),
(@category_id, '首诊检查', 'S', '首诊角膜检查结果', 1, NOW(), NOW()),
(@category_id, '首诊检查', 'S', '首诊前房检查结果', 1, NOW(), NOW()),
(@category_id, '首诊检查', 'S', '首诊玻璃体及眼底检查结果', 1, NOW(), NOW()),
(@category_id, '首诊检查', 'S', '既往是否使用眼部治疗药物', 1, NOW(), NOW()),
(@category_id, '首诊检查', 'S', '是否有药物过敏史', 1, NOW(), NOW()),

-- 首诊感染指标评估（评分题）
(@category_id, '首诊感染指标', 'P', '首诊畏光程度评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '首诊感染指标', 'P', '首诊异物感程度评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '首诊感染指标', 'P', '首诊结膜充血程度评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '首诊感染指标', 'P', '首诊分泌物程度评分（0-3分）', 1, NOW(), NOW()),

-- 用药方案相关
(@category_id, '用药方案', 'S', '加替沙星眼用凝胶每日使用次数', 1, NOW(), NOW()),
(@category_id, '用药方案', 'S', '是否合并使用其他眼部药物', 1, NOW(), NOW()),

-- 七天复查相关问题
(@category_id, '复查检查', 'S', '复查结膜检查结果', 1, NOW(), NOW()),
(@category_id, '复查检查', 'S', '复查角膜检查结果', 1, NOW(), NOW()),
(@category_id, '复查检查', 'S', '复查前房检查结果', 1, NOW(), NOW()),
(@category_id, '复查检查', 'S', '复查玻璃体及眼底检查结果', 1, NOW(), NOW()),

-- 复查感染指标评估（评分题）
(@category_id, '复查感染指标', 'P', '复查畏光程度评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '复查感染指标', 'P', '复查异物感程度评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '复查感染指标', 'P', '复查结膜充血程度评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '复查感染指标', 'P', '复查分泌物程度评分（0-3分）', 1, NOW(), NOW()),

-- 疗效评估
(@category_id, '疗效评估', 'S', '本次感染治疗效果判定', 1, NOW(), NOW()),

-- 安全性评估（评分题）
(@category_id, '安全性评估', 'P', '眼部耐受性评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '安全性评估', 'P', '烧灼感程度评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '安全性评估', 'P', '眼刺痛程度评分（0-3分）', 1, NOW(), NOW()),
(@category_id, '安全性评估', 'S', '视力质量变化情况', 1, NOW(), NOW()),

-- 药物不良反应评估
(@category_id, '不良反应', 'S', '结膜刺激、流泪程度', 1, NOW(), NOW()),
(@category_id, '不良反应', 'S', '角膜炎和乳头状结膜炎程度', 1, NOW(), NOW()),
(@category_id, '不良反应', 'S', '是否有其他不良反应症状', 1, NOW(), NOW());

-- 3. 插入选项数据（需要根据实际问题ID调整）

-- 为了方便管理，我们先获取问题ID
SET @q1 = (SELECT id FROM survey_questionbank WHERE title = '患者性别' AND category_id = @category_id);
SET @q2 = (SELECT id FROM survey_questionbank WHERE title = '是否进行手术' AND category_id = @category_id);
SET @q3 = (SELECT id FROM survey_questionbank WHERE title = '研究眼别（如已手术）' AND category_id = @category_id);
SET @q4 = (SELECT id FROM survey_questionbank WHERE title = '手术方式（如已手术）' AND category_id = @category_id);
SET @q5 = (SELECT id FROM survey_questionbank WHERE title = '首诊结膜检查结果' AND category_id = @category_id);
SET @q6 = (SELECT id FROM survey_questionbank WHERE title = '首诊角膜检查结果' AND category_id = @category_id);
SET @q7 = (SELECT id FROM survey_questionbank WHERE title = '首诊前房检查结果' AND category_id = @category_id);
SET @q8 = (SELECT id FROM survey_questionbank WHERE title = '首诊玻璃体及眼底检查结果' AND category_id = @category_id);
SET @q9 = (SELECT id FROM survey_questionbank WHERE title = '既往是否使用眼部治疗药物' AND category_id = @category_id);
SET @q10 = (SELECT id FROM survey_questionbank WHERE title = '是否有药物过敏史' AND category_id = @category_id);

-- 评分题选项
SET @q11 = (SELECT id FROM survey_questionbank WHERE title = '首诊畏光程度评分（0-3分）' AND category_id = @category_id);
SET @q12 = (SELECT id FROM survey_questionbank WHERE title = '首诊异物感程度评分（0-3分）' AND category_id = @category_id);
SET @q13 = (SELECT id FROM survey_questionbank WHERE title = '首诊结膜充血程度评分（0-3分）' AND category_id = @category_id);
SET @q14 = (SELECT id FROM survey_questionbank WHERE title = '首诊分泌物程度评分（0-3分）' AND category_id = @category_id);

SET @q15 = (SELECT id FROM survey_questionbank WHERE title = '加替沙星眼用凝胶每日使用次数' AND category_id = @category_id);
SET @q16 = (SELECT id FROM survey_questionbank WHERE title = '是否合并使用其他眼部药物' AND category_id = @category_id);

-- 复查相关
SET @q17 = (SELECT id FROM survey_questionbank WHERE title = '复查结膜检查结果' AND category_id = @category_id);
SET @q18 = (SELECT id FROM survey_questionbank WHERE title = '复查角膜检查结果' AND category_id = @category_id);
SET @q19 = (SELECT id FROM survey_questionbank WHERE title = '复查前房检查结果' AND category_id = @category_id);
SET @q20 = (SELECT id FROM survey_questionbank WHERE title = '复查玻璃体及眼底检查结果' AND category_id = @category_id);

-- 复查评分题
SET @q21 = (SELECT id FROM survey_questionbank WHERE title = '复查畏光程度评分（0-3分）' AND category_id = @category_id);
SET @q22 = (SELECT id FROM survey_questionbank WHERE title = '复查异物感程度评分（0-3分）' AND category_id = @category_id);
SET @q23 = (SELECT id FROM survey_questionbank WHERE title = '复查结膜充血程度评分（0-3分）' AND category_id = @category_id);
SET @q24 = (SELECT id FROM survey_questionbank WHERE title = '复查分泌物程度评分（0-3分）' AND category_id = @category_id);

-- 疗效和安全性
SET @q25 = (SELECT id FROM survey_questionbank WHERE title = '本次感染治疗效果判定' AND category_id = @category_id);
SET @q26 = (SELECT id FROM survey_questionbank WHERE title = '眼部耐受性评分（0-3分）' AND category_id = @category_id);
SET @q27 = (SELECT id FROM survey_questionbank WHERE title = '烧灼感程度评分（0-3分）' AND category_id = @category_id);
SET @q28 = (SELECT id FROM survey_questionbank WHERE title = '眼刺痛程度评分（0-3分）' AND category_id = @category_id);
SET @q29 = (SELECT id FROM survey_questionbank WHERE title = '视力质量变化情况' AND category_id = @category_id);

-- 不良反应
SET @q30 = (SELECT id FROM survey_questionbank WHERE title = '结膜刺激、流泪程度' AND category_id = @category_id);
SET @q31 = (SELECT id FROM survey_questionbank WHERE title = '角膜炎和乳头状结膜炎程度' AND category_id = @category_id);
SET @q32 = (SELECT id FROM survey_questionbank WHERE title = '是否有其他不良反应症状' AND category_id = @category_id);

-- 插入选项数据
INSERT INTO survey_option (question_id, title, `order`, created_at, updated_at) VALUES 

-- 患者性别选项
(@q1, '男', 1, NOW(), NOW()),
(@q1, '女', 0, NOW(), NOW()),

-- 是否手术选项
(@q2, '否', 1, NOW(), NOW()),
(@q2, '是', 0, NOW(), NOW()),

-- 研究眼别选项
(@q3, '右眼', 1, NOW(), NOW()),
(@q3, '左眼', 0, NOW(), NOW()),

-- 手术方式（填空题选项）
(@q4, '手术方式描述', 0, NOW(), NOW()),

-- 首诊结膜检查结果选项
(@q5, '正常', 1, NOW(), NOW()),
(@q5, '异常', 0, NOW(), NOW()),

-- 首诊角膜检查结果选项
(@q6, '正常', 1, NOW(), NOW()),
(@q6, '异常', 0, NOW(), NOW()),

-- 首诊前房检查结果选项
(@q7, '正常', 1, NOW(), NOW()),
(@q7, '异常', 0, NOW(), NOW()),

-- 首诊玻璃体及眼底检查结果选项
(@q8, '正常', 1, NOW(), NOW()),
(@q8, '异常', 0, NOW(), NOW()),

-- 既往眼部用药史选项
(@q9, '无', 1, NOW(), NOW()),
(@q9, '有', 0, NOW(), NOW()),

-- 药物过敏史选项
(@q10, '无', 1, NOW(), NOW()),
(@q10, '有', 0, NOW(), NOW()),

-- 评分题选项（0-3分）
(@q11, '0分', 3, NOW(), NOW()),
(@q11, '1分', 2, NOW(), NOW()),
(@q11, '2分', 1, NOW(), NOW()),
(@q11, '3分', 0, NOW(), NOW()),

(@q12, '0分', 3, NOW(), NOW()),
(@q12, '1分', 2, NOW(), NOW()),
(@q12, '2分', 1, NOW(), NOW()),
(@q12, '3分', 0, NOW(), NOW()),

(@q13, '0分', 3, NOW(), NOW()),
(@q13, '1分', 2, NOW(), NOW()),
(@q13, '2分', 1, NOW(), NOW()),
(@q13, '3分', 0, NOW(), NOW()),

(@q14, '0分', 3, NOW(), NOW()),
(@q14, '1分', 2, NOW(), NOW()),
(@q14, '2分', 1, NOW(), NOW()),
(@q14, '3分', 0, NOW(), NOW()),

-- 每日用药次数选项
(@q15, '每日1次', 3, NOW(), NOW()),
(@q15, '每日2次', 2, NOW(), NOW()),
(@q15, '每日3次', 1, NOW(), NOW()),
(@q15, '每日4次', 0, NOW(), NOW()),

-- 是否合并用药选项
(@q16, '无', 1, NOW(), NOW()),
(@q16, '有', 0, NOW(), NOW()),

-- 复查结膜检查结果选项
(@q17, '正常', 1, NOW(), NOW()),
(@q17, '异常', 0, NOW(), NOW()),

-- 复查角膜检查结果选项
(@q18, '正常', 1, NOW(), NOW()),
(@q18, '异常', 0, NOW(), NOW()),

-- 复查前房检查结果选项
(@q19, '正常', 1, NOW(), NOW()),
(@q19, '异常', 0, NOW(), NOW()),

-- 复查玻璃体及眼底检查结果选项
(@q20, '正常', 1, NOW(), NOW()),
(@q20, '异常', 0, NOW(), NOW()),

-- 复查评分题选项（0-3分）
(@q21, '0分', 3, NOW(), NOW()),
(@q21, '1分', 2, NOW(), NOW()),
(@q21, '2分', 1, NOW(), NOW()),
(@q21, '3分', 0, NOW(), NOW()),

(@q22, '0分', 3, NOW(), NOW()),
(@q22, '1分', 2, NOW(), NOW()),
(@q22, '2分', 1, NOW(), NOW()),
(@q22, '3分', 0, NOW(), NOW()),

(@q23, '0分', 3, NOW(), NOW()),
(@q23, '1分', 2, NOW(), NOW()),
(@q23, '2分', 1, NOW(), NOW()),
(@q23, '3分', 0, NOW(), NOW()),

(@q24, '0分', 3, NOW(), NOW()),
(@q24, '1分', 2, NOW(), NOW()),
(@q24, '2分', 1, NOW(), NOW()),
(@q24, '3分', 0, NOW(), NOW()),

-- 治疗效果判定选项
(@q25, '痊愈', 3, NOW(), NOW()),
(@q25, '显效', 2, NOW(), NOW()),
(@q25, '有效', 1, NOW(), NOW()),
(@q25, '无效', 0, NOW(), NOW()),

-- 安全性评估评分题选项（0-3分）
(@q26, '0分', 3, NOW(), NOW()),
(@q26, '1分', 2, NOW(), NOW()),
(@q26, '2分', 1, NOW(), NOW()),
(@q26, '3分', 0, NOW(), NOW()),

(@q27, '0分', 3, NOW(), NOW()),
(@q27, '1分', 2, NOW(), NOW()),
(@q27, '2分', 1, NOW(), NOW()),
(@q27, '3分', 0, NOW(), NOW()),

(@q28, '0分', 3, NOW(), NOW()),
(@q28, '1分', 2, NOW(), NOW()),
(@q28, '2分', 1, NOW(), NOW()),
(@q28, '3分', 0, NOW(), NOW()),

-- 视力质量变化选项
(@q29, '视觉质量有提高', 1, NOW(), NOW()),
(@q29, '视觉质量无改变', 0, NOW(), NOW()),

-- 不良反应程度选项
(@q30, '无', 3, NOW(), NOW()),
(@q30, '轻', 2, NOW(), NOW()),
(@q30, '中', 1, NOW(), NOW()),
(@q30, '重', 0, NOW(), NOW()),

(@q31, '无', 3, NOW(), NOW()),
(@q31, '轻', 2, NOW(), NOW()),
(@q31, '中', 1, NOW(), NOW()),
(@q31, '重', 0, NOW(), NOW()),

-- 其他症状选项
(@q32, '无', 1, NOW(), NOW()),
(@q32, '有', 0, NOW(), NOW());

-- 显示插入结果
SELECT 
    '问卷分类ID:' as '结果',
    @category_id as '值'
UNION ALL
SELECT 
    '插入问题数量:' as '结果',
    COUNT(*) as '值'
FROM survey_questionbank 
WHERE category_id = @category_id
UNION ALL
SELECT 
    '插入选项数量:' as '结果',
    COUNT(*) as '值'
FROM survey_option o
JOIN survey_questionbank q ON o.question_id = q.id
WHERE q.category_id = @category_id;
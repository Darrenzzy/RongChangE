from datetime import datetime

import pandas as pd
from collections import defaultdict


def analysis_excel(file: str):
    """
    读取后台导出的调研提交记录分析：
        - 统计各分类下 各题目下的答 案选择统计率
    """
    df = pd.read_excel(file)  # 替换为你的文件路径

    # 动态确定题目数量
    question_columns = [col for col in df.columns if col.startswith('题目')]
    num_questions = len(question_columns)

    # 准备存储结果的字典
    results = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    category_totals = defaultdict(lambda: defaultdict(int))
    question_positions = defaultdict(lambda: defaultdict(set))  # 存储题目位置

    # 遍历每一行数据
    for _, row in df.iterrows():
        category = row['分类']

        # 遍历每个题目
        for i in range(1, num_questions + 1):
            question = row[f'题目{i}']
            answer = row[f'答案{i}']

            # 跳过空题目或空答案
            if pd.isna(question) or pd.isna(answer):
                continue

            # 记录题目位置
            question_positions[category][question].add(i)

            # 更新总回答数（每个题目计数一次）
            category_totals[category][question] += 1

            # 处理多选题（分号分隔的答案）
            if isinstance(answer, str) and ';' in answer:
                # 拆分多选题答案
                answers = [ans.strip() for ans in answer.split(';') if ans.strip()]
                for ans in answers:
                    results[category][question][ans] += 1
            else:
                # 处理单选题或非字符串答案
                if not isinstance(answer, str):
                    answer = str(answer)  # 确保答案为字符串类型
                results[category][question][answer] += 1

    # 创建最终结果DataFrame
    final_data = []

    for category, questions in results.items():
        for question, answers in questions.items():
            total = category_totals[category][question]

            # 获取题目位置并排序
            positions = sorted(question_positions[category][question])
            position_str = ';'.join(map(str, positions))

            for answer, count in answers.items():
                percentage = round((count / total) * 100, 2)
                final_data.append({
                    '分类': category,
                    '题目': question,
                    '题目位置': position_str,  # 新增字段
                    '答案选项': answer,
                    '选择次数': count,
                    '题目总回答数': total,
                    '选择率(%)': percentage
                })

    # 创建DataFrame并排序
    result_df = pd.DataFrame(final_data)
    result_df = result_df.sort_values(['分类', '题目', '选择次数'],
                                      ascending=[True, True, False])

    # 保存结果
    result_df.to_excel(f'./题目答案统计-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx', index=False)

    print("统计完成！结果已保存到'题目答案统计.xlsx'")
    print(f"共处理 {len(df)} 条记录，{num_questions} 道题目")


if __name__ == '__main__':
    analysis_excel(r"./提交记录-rebuild.xlsx")

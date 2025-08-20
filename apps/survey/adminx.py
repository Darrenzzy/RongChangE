#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: adminx.py

@author: 'ovan'

@mtime: '2024/7/30'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import json
import logging

import pandas
import sqlparse
from django.conf import settings
from django.contrib import messages
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.utils.datetime_safe import datetime
from pandas import DataFrame

from agreement.models import LaborFeeLevel
from survey.models import DiseasesCategory, CommitLog, QuestionBank, Option
from vendor.abnormal.fmt_log_exception import fmt_error
from vendor.connection import read_sql_with_pandas
from vendor.storage.local_storage.file import django_storage_save
from works.models import WorksState
from xadmin.excel_response import get_admin_excel_response
from xadmin.forms import get_ip_address
from xadmin.layout import Main, Fieldset
from xadmin.sites import register, short_description
from xadmin.util import create_event_log

log_except = logging.getLogger('except')


@register(DiseasesCategory)
class DiseasesCategoryAdmin(object):
    list_display = ["id", "title", "order", "is_use", 'created_at']
    list_filter = ["order", "is_use"]
    search_fields = ["title", ]
    list_editable = ['is_use']


class OptionInline(object):
    model = Option
    extra = 0


@register(QuestionBank)
class QuestionBankAdmin(object):
    list_display = ["id", "category", "scope", "kind", "title", "is_use", 'created_at']
    list_filter = ["kind", "category__title", "is_use", 'created_at']
    search_fields = ["title", ]
    inlines = [OptionInline, ]
    list_editable = ['is_use']

    import_excel = True
    excel_template_uri = 'https://rcmyhg-qn.yuemia.com/media/1722585127488/荣昌合规调研题库导入_V1_0731.xlsx'

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            excel_data = request.FILES['excel']
            current_uri = request.build_absolute_uri()

            try:
                django_storage_save(location=settings.PRIVATE_UPLOAD_FILE_ROOT, name=excel_data.name, file=excel_data)
            except Exception as e:
                fmt_error(
                    log_except, title=f"题库导入 x-admin 界面存储文件异常, {current_uri}", e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "题库导入"],
                    request=request
                )
                messages.add_message(request, messages.ERROR, "EXCEL文件异常")
                return HttpResponseRedirect(current_uri)

            try:
                excel_reader = pandas.ExcelFile(excel_data, "openpyxl")
                sheet_names = excel_reader.sheet_names
            except Exception as _:
                messages.add_message(request, messages.ERROR, "无效Excel文件")
                return HttpResponseRedirect(current_uri)

            records = {
                "func": parse_question_import_func,
                "fields": ["疾病分类", "调研范围", "题型", "题目"],
                "dtype": {"疾病分类": str, "调研范围": str, "题型": str, "题目": str, },
            }
            for sheet in sheet_names:
                data = excel_reader.parse(sheet_name=sheet, dtype=records['dtype'])
                data.replace('空', '', inplace=True)
                shape_ = data.shape[0]
                template_head_ = data.columns.tolist()
                if (
                        (shape_ == 0) or (len(template_head_) < 4) or (template_head_[:4] != records['fields'])
                        or (len([x for x in template_head_[4:] if not x.startswith("选项")]) > 0)
                ):
                    messages.add_message(
                        request, messages.ERROR,
                        f"SHEET {sheet} 表头格式不规范; {template_head_}, 正确表头字段：{records['fields']} + 选项A/B/C/..."
                    )
                    return HttpResponseRedirect(current_uri)

                # validate db
                try:
                    records['func'](data, shape_, sheet, request)
                except Exception as e:
                    fmt_error(
                        log_except, title=f"题库导入 x-admin {sheet} 数据存储写入异常, {current_uri}", e=e,
                        other={"filename": excel_data.name},
                        tag=["x-admin导入功能", "题库写入"],
                        request=request
                    )
                    messages.add_message(
                        request, messages.ERROR,
                        f"SHEET {sheet} 导入存储写入异常:{e}"
                    )
                    return HttpResponseRedirect(current_uri)

        return super().post(request, *args, **kwargs)


question_bank_kind_map = {"单选题": "S", "多选题": "D", "评分题": "P", "排序题": "T", }
kind_map = {"S": "单选题", "D": "多选题", "P": "评分题", "T": "排序题", }


def parse_question_import_func(
        data: DataFrame,
        shape: int,
        sheet: str,
        request
):
    success_num = 0
    comm_str = f"SHEET {sheet} 共计读取{shape}条数据，"
    category_map = {x['title']: x['id'] for x in DiseasesCategory.objects.values("id", "title")}

    # 疾病分类异常
    not_exist_category = {}
    # 题目类型异常
    not_exist_kind = {}
    # 题目标题、选项标题过长问题
    title_field_length_error = 0

    for index, row in data.fillna("").iterrows():
        row_dict = row.to_dict()
        category_id = category_map.get(row_dict['疾病分类'], None)
        if not category_id:
            if row_dict['疾病分类'] in not_exist_category:
                not_exist_category[row_dict['疾病分类']] += 1
            else:
                not_exist_category[row_dict['疾病分类']] = 0
            continue

        kind = question_bank_kind_map.get(row_dict['题型'], None)
        if not kind:
            if row_dict['题目'] in not_exist_kind:
                not_exist_kind[row_dict['题目']] += 1
            else:
                not_exist_kind[row_dict['题目']] = 0
            continue

        try:
            with atomic():
                obj = QuestionBank.objects.create(
                    category_id=category_id, scope=row_dict['调研范围'], kind=kind, title=row_dict['题目']
                )
                # 将选项dict过滤出来
                Option.objects.bulk_create(
                    [
                        Option(
                            question_id=obj.pk,
                            title=value,
                        )
                        for key, value in row_dict.items() if key.startswith("选项") and value
                    ]
                )
                success_num += 1
        except Exception as e:
            title_field_length_error += 1

            fmt_error(
                log_except, title=f"题库导入 x-admin {sheet} 题目数据存储异常 ", e=e,
                other={"row_dict": row_dict},
                tag=["x-admin导入功能", "题库导入题目入库异常"],
                request=request
            )

    comm_str += f"成功写入题目数据{success_num}条。"
    if title_field_length_error > 0:
        comm_str += f"题目标题、选项标题过长问题{title_field_length_error}条。"

    if len(not_exist_category) > 0:
        comm_str += f"疾病分类不存在{len(not_exist_category)}条。"
        for key, value in not_exist_category.items():
            comm_str += f"疾病分类 {key}: {value}条。"

    if len(not_exist_kind) > 0:
        comm_str += f"题目类型不存在{len(not_exist_kind)}条。"

    messages.add_message(
        request, messages.SUCCESS,
        comm_str
    )


# (("S", "单选题"), ("D", "多选题"), ("P", "评分题"), ("T", "排序题"))
option_kind_map = {
    "S": "单选题",
    "D": "多选题",
    "P": "评分题",
    "T": "排序题",
}


def expand_submitted_data(_df: DataFrame):
    max_columns = 0  # 记录最大问题数量

    # 遍历处理每条记录的提交数据
    expanded_data = []
    for idx, row in _df.iterrows():
        try:
            # qa_list = json.loads(row['提交数据'])
            qa_list = row['提交数据']
            qa_dict = {}
            for i, qa in enumerate(qa_list, 1):
                qa_dict[f'题目{i}'] = (f"【类型：{option_kind_map.get(qa.get('kind', ''), '-')}】"
                                       f"【范围：{qa.get('scope', '')}】 标题： {qa.get('title', '')}")
                # 处理答案组合（允许多选答案）
                qa_dict[f'答案{i}'] = ';'.join([opt['title'] for opt in qa.get('options', [])])
            max_columns = max(max_columns, len(qa_list))
            expanded_data.append(qa_dict)
        except Exception as e:
            expanded_data.append({})
            log_except.error(f"解析第{idx}行失败: {str(e)}", exc_info=True)

    # 创建固定列数的DataFrame
    return pandas.DataFrame(
        expanded_data, columns=[f'{pre}{i}' for i in range(1, max_columns + 1) for pre in ('题目', '答案')]
    )


@register(CommitLog)
class CommitLogAdmin(object):
    readonly_fields = ["category", "user", ]
    list_display = ["id", "category", "get_name", "get_province", "phone",
                    "level", "state", 'payment_time', 'payment_amount', "created_at"]
    list_filter = ["category__title", "level__level", "state__title", 'created_at']
    search_fields = ["phone", ]
    change_form_template = "model_form.html"
    list_exclude = ["hospital", ]

    show_bookmarks = True
    list_bookmarks = [
        {'title': "空状态过滤", 'query': {'state_id__isnull': True}, },
        {'title': "非空状态过滤", 'query': {'state_id__isnull': False}, },
    ]

    def queryset(self):
        return super().queryset().select_related("user", 'category', 'level', 'state')

    @short_description("医生姓名")
    def get_name(self, obj):
        return (obj.user.name or '-') if obj.user_id else "未填写"

    @short_description("省份")
    def get_province(self, obj):
        return (obj.user.province or '-') if obj.user_id else "未填写"

    # @short_description("大区")
    # def get_region(self, obj):
    #     return (obj.user.region or '-') if obj.user_id else "未填写"
    #
    # @short_description("片区")
    # def get_precinct(self, obj):
    #     return (obj.user.precinct or '-') if obj.user_id else "未填写"

    # def has_add_permission(self, request=None, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request=None, obj=None):
    #     return False

    def get_context(self):
        context = super().get_context()
        if hasattr(self, 'org_obj') and self.org_obj and hasattr(self.org_obj, 'data') and self.org_obj.data is not None:
            _dt = self.org_obj.data
            if _dt:
                for index, x in enumerate(_dt):  x["index"], x['kind'] = index + 1, kind_map.get(x['kind'])

            context.update({
                "commit_log_json": _dt
            })
        return context

    def get_form_layout(self):
        if self.org_obj:
            self.form_layout = (
                Main(
                    Fieldset(
                        '',
                        'user', 'category', 'phone', 'level', 'state', 'payment_time', 'payment_amount',
                        css_class='unsort no_title'
                    ),

                ),

            )
        return super().get_form_layout()

    import_excel = True
    excel_template_uri = 'https://rcmyhg-qn.yuemia.com/media/1727417541782/调研提交记录批量状态维护-template-v1-2024.xlsx'

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            excel_data = request.FILES['excel']
            current_uri = request.build_absolute_uri()
            location = settings.PRIVATE_UPLOAD_FILE_ROOT / 'survey_commit_history'

            try:
                django_storage_save(location=location, name=excel_data.name, file=excel_data)
            except Exception as e:
                fmt_error(
                    log_except, title=f"调研提交记录批量状态维护 x-admin 界面存储文件异常, {current_uri}", e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "调研提交记录批量状态维护"],
                    request=request
                )
                messages.add_message(request, messages.ERROR, "EXCEL文件异常")
                return HttpResponseRedirect(current_uri)

            try:
                excel_reader = pandas.ExcelFile(excel_data, "openpyxl")
                sheet_names = excel_reader.sheet_names
            except Exception as _:
                messages.add_message(request, messages.ERROR, "无效Excel文件")
                return HttpResponseRedirect(current_uri)

            records = {
                "func": parse_survey_commit_history_import_func,
                "dtype": {"ID": int, "状态": str, '劳务费档位': str, '支付时间': str, '支付金额': float},
            }
            #
            sheet = "调研提交记录批量状态维护"
            if sheet not in sheet_names:
                messages.add_message(request, messages.ERROR, f"Excel文件不存在sheet {sheet}表")
                return HttpResponseRedirect(current_uri)

            data = excel_reader.parse(sheet_name=sheet, dtype=records['dtype'])
            data.replace('空', '', inplace=True)
            shape_ = data.shape[0]
            template_head_ = data.columns.tolist()
            if (
                    (shape_ == 0) or ("ID" not in template_head_) or ("状态" not in template_head_)
                    or ("劳务费档位" not in template_head_) or ("支付时间" not in template_head_)
                    or ("支付金额" not in template_head_)
            ):
                messages.add_message(
                    request, messages.ERROR,
                    f"SHEET {sheet} 表头格式不规范; {template_head_}, 正确表头字段应当包含ID、状态、劳务费档位、支付时间、支付金额字段。"
                )
                return HttpResponseRedirect(current_uri)

            # validate db
            try:
                records['func'](data=data, shape=shape_, sheet=sheet, request=request, opts=self.opts)
            except Exception as e:
                fmt_error(
                    log_except, title=f"调研提交记录批量状态维护 x-admin {sheet} 数据存储写入异常, {current_uri}", e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "调研提交记录批量状态维护"],
                    request=request
                )
                messages.add_message(
                    request, messages.ERROR,
                    f"SHEET {sheet} 导入存储写入异常:{e}"
                )
                return HttpResponseRedirect(current_uri)

        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        _params = request.GET
        if _params.get("_do_") == "export" and self.has_export_permission():
            response = self.get_result_list()
            if response:
                return response

            queryset = self.result_list
            sql, params = queryset.query.sql_with_params()
            parsed = sqlparse.parse(sql)[0]
            for token in parsed.tokens:
                _temp_token_str = str(token)
                if (
                        ("ASC" not in _temp_token_str)
                        and ("DESC" not in _temp_token_str)
                        and isinstance(token, sqlparse.sql.IdentifierList)
                ):
                    # 修改 SELECT 子句
                    new_select_clause = """
`survey_commitlog`.`id` as 'ID',
`survey_diseasescategory`.`title` as '分类' ,
`user_doctor`.`name` as '医生姓名' ,
`user_doctor`.`province` as '省份' ,
`survey_commitlog`.`phone` as '手机号',
`agreement_laborfeelevel`.`level` as '劳务费档位-档位',
`agreement_laborfeelevel`.`state` as '劳务费档位-状态',
`works_worksstate`.`title` as '状态',
`survey_commitlog`.`payment_time` as '支付时间' ,
`survey_commitlog`.`payment_amount` as '支付金额' ,
`survey_commitlog`.`hospital` as '医院',
`survey_commitlog`.`created_at` as '创建时间' ,
`survey_commitlog`.`updated_at` as '更新时间',
`survey_commitlog`.`data` as '提交数据'
                    """
                    token.tokens = sqlparse.parse(new_select_clause)[0].tokens

            df = read_sql_with_pandas(sql=str(parsed), params=params)
            if not df.empty:
                df['劳务费档位-状态'] = df['劳务费档位-状态'].map({1: '激活', 2: "禁用"})
                df['提交数据'] = df['提交数据'].apply(json.loads)
                df_expanded = expand_submitted_data(df)
                df = pandas.concat([df.drop('提交数据', axis=1), df_expanded], axis=1)

            filename = CommitLog._meta.verbose_name
            return get_admin_excel_response(
                request=request,
                opts=self.opts,
                filename=filename,
                data_frame=df,
            )
        return super().get(request, *args, **kwargs)


def parse_survey_commit_history_import_func(
        data: DataFrame,
        shape: int,
        sheet: str,
        request,
        opts,
):
    """
    解析导入文件-调研提交记录批量状态维护
    """

    success_map, error_map = {}, {}
    comm_str = f"SHEET {sheet} 共计读取{shape}条数据，"
    state_query = WorksState.objects.values("id", "title")
    category_map = {x['title']: x['id'] for x in state_query}
    state_map = {x['id']: x['title'] for x in state_query}

    update_str = []
    # 劳务费档位
    level_query = LaborFeeLevel.objects.all()
    level_map = {x.__str__(): x.id for x in level_query}
    level_title_map = {x.id: x.__str__() for x in level_query}

    # 状态异常
    not_exist_category = {}
    # 劳务费异常
    not_exist_level = {}
    for index, row in data.fillna("").iterrows():
        row_dict = row.to_dict()
        level_id = level_map.get(row_dict['劳务费档位'], None)
        category_id = category_map.get(row_dict['状态'], None)

        if not category_id:
            if row_dict['状态'] in not_exist_category:
                not_exist_category[row_dict['状态']] += 1
            else:
                not_exist_category[row_dict['状态']] = 0

        if not level_id:
            if row_dict['劳务费档位'] in not_exist_level:
                not_exist_level[row_dict['劳务费档位']] += 1
            else:
                not_exist_level[row_dict['劳务费档位']] = 0
        update_payment_time = datetime.strptime(row_dict['支付时间'], "%Y年%m月%d日 %H:%M") \
            if row_dict['支付时间'] else None

        try:
            with atomic():
                obj = CommitLog.objects.filter(id=row_dict['ID']).first()
                if obj:
                    update_fields = []

                    level_id_change = obj.level_id != level_id
                    category_id_change = obj.state_id != category_id
                    payment_time_change = obj.payment_time != update_payment_time
                    amount_change = obj.payment_amount != row_dict['支付金额']

                    success_map[row_dict['ID']] = {
                        "index": index,
                        # 状态
                        'state_is_change': category_id_change,
                        "new_state_id": category_id, "new_state_title": row_dict['状态'],
                        "old_state_id": obj.state_id, "old_state_title": state_map.get(obj.state_id, '-'),

                        # 劳务费档位
                        'level_is_change': level_id_change,
                        "new_level_id": level_id, "new_level_title": row_dict['劳务费档位'],
                        "old_level_id": obj.level_id, "old_level_title": level_title_map.get(obj.level_id, '-'),

                        # 支付时间
                        "payment_time_is_change": payment_time_change,
                        "new_payment_time": str(update_payment_time),
                        "old_payment_time": str(obj.payment_time),

                        # 支付金额
                        "amount_is_change": amount_change,
                        "new_payment_amount": row_dict['支付金额'],
                        "old_payment_amount": str(obj.payment_amount),
                    }

                    if level_id_change:
                        obj.level_id = level_id
                        update_fields.append('level_id')
                        update_str.append(
                            f"[{obj.id}] 劳务费档位由 [{level_title_map.get(obj.level_id, '-')}] 修改为 [{row_dict['劳务费档位']}]"
                        )
                    if category_id_change:
                        obj.state_id = category_id
                        update_fields.append('state_id')
                        update_str.append(
                            f"[{obj.id}] 状态由 [{state_map.get(obj.state_id, '-')}] 修改为 [{row_dict['状态']}]")

                    if payment_time_change:
                        obj.payment_time = update_payment_time
                        update_fields.append('payment_time')
                        update_str.append(f"[{obj.id}] 支付时间由 [{obj.payment_time}] 修改为 [{update_payment_time}]")

                    if amount_change:
                        obj.payment_amount = row_dict['支付金额']
                        update_fields.append('payment_amount')
                        update_str.append(
                            f"[{obj.id}] 支付金额由 [{obj.payment_amount}] 修改为 [{row_dict['支付金额']}]")

                    if len(update_fields) > 0:
                        obj.save()
                else:
                    error_map[row_dict['ID']] = {
                        "index": index,
                        "error": f"{row_dict['ID']} 数据不存在",
                        "new_state_id": category_id, "new_state_title": row_dict['状态'],
                        "old_state_id": None, "old_state_title": None,
                        'row_dict': row_dict,
                    }
        except Exception as e:
            error_map[row_dict['ID']] = {
                "index": index,
                "error": f"{row_dict['ID']} 数据不存在",
                "e": str(e),
                "new_state_id": category_id, "new_state_title": row_dict['状态'],
                "old_state_id": None, "old_state_title": None,
                'row_dict': row_dict,
            }
            fmt_error(
                log_except, title=f"调研提交记录批量状态维护 x-admin {sheet} 状态数据存储异常 ", e=e,
                other={"row_dict": row_dict},
                tag=["x-admin导入功能", "调研提交记录批量状态维护异常"],
                request=request
            )

    comm_str += f'成功更新{len(success_map)}条，失败{len(error_map)}条。'
    if len(not_exist_category) > 0:
        comm_str += f"失败原因：后台状态不存在{len(not_exist_category)}条，请先在后台状态中先创建。"
        for key, value in not_exist_category.items():
            comm_str += f"状态 {key}: {value}条。"
    if len(not_exist_level) > 0:
        comm_str += f"失败原因：后台劳务费不存在{len(not_exist_level)}条，请先在后台劳务费中先创建。"
        for key, value in not_exist_level.items():
            comm_str += f"劳务费 {key}: {value}条。"

    create_event_log(
        flag="import", message=f"导入 [{sheet}] xlsx-格式, {comm_str}",
        user=request.user, ip_addr=get_ip_address(request), app_label=opts.app_label,
        model_name=opts.model_name,
        obj=None, object_repr=None, original_data=None,
        new_data={'update_str': update_str, "success_map": success_map, "error_map": error_map}
    )
    messages.add_message(
        request, messages.SUCCESS,
        comm_str
    )

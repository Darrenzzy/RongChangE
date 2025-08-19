import logging
from datetime import datetime

import pandas
from django.conf import settings
from django.contrib import messages
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from pandas import DataFrame

from agreement.models import LaborFeeLevel
from vendor.abnormal.fmt_log_exception import fmt_error
from vendor.storage.local_storage.file import django_storage_save
from works.models import Works, WorksCategory, WorksState, CaseWorksState, Case, Disease, Question, Item, MedCase, \
    QuestionKindChoices
from xadmin.forms import get_ip_address
from xadmin.layout import Main, Fieldset
from xadmin.sites import register, short_description
from xadmin.util import create_event_log

log_except = logging.getLogger('except')


@register(WorksCategory)
class WorksCategoryAdmin(object):
    list_display = ['title', 'order']


@register(WorksState)
class WorksStateAdmin(object):
    list_display = ['title', 'order']


@register(Works)
class WorksAdmin(object):
    list_display = ['id', 'title', 'author_name', 'phone', 'category', 'level', 'state', 'payment_time',
                    'payment_amount', 'is_push', 'created_at']
    list_filter = ['category', 'state', 'payment_time', 'payment_amount', 'is_push', 'level', 'created_at']
    search_fields = ['title', 'phone', 'author__name', 'hospital']
    style_fields = {
        'content': 'ueditor',
    }
    list_editable = ['is_push']
    list_exclude = ['hospital', ]

    @short_description('作者姓名')
    def author_name(self, instance):
        return instance.author.name

    def queryset(self):
        _queryset = super().queryset()
        return _queryset.select_related('author', 'level', 'category', 'state', )

    import_excel = True
    excel_template_uri = 'https://rcmyhg-qn.yuemia.com/media/1727417541782/作品管理批量状态维护-template-v1-2024.xlsx'

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            excel_data = request.FILES['excel']
            current_uri = request.build_absolute_uri()
            location = settings.PRIVATE_UPLOAD_FILE_ROOT / 'works_history'

            try:
                django_storage_save(location=location, name=excel_data.name, file=excel_data)
            except Exception as e:
                fmt_error(
                    log_except, title=f"作品管理批量状态维护 x-admin 界面存储文件异常, {current_uri}", e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "作品管理批量状态维护"],
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
                "func": parse_works_history_import_func,
                "dtype": {"ID": int, "状态": str, '劳务费档位': str, '支付时间': str, '支付金额': float},
            }
            #
            sheet = "作品管理批量状态维护"
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
                    log_except, title=f"作品管理批量状态维护 x-admin {sheet} 数据存储写入异常, {current_uri}",
                    e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "作品管理批量状态维护"],
                    request=request
                )
                messages.add_message(
                    request, messages.ERROR,
                    f"SHEET {sheet} 导入存储写入异常:{e}"
                )
                return HttpResponseRedirect(current_uri)

        return super().post(request, *args, **kwargs)


def parse_works_history_import_func(
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
                obj = Works.objects.filter(id=row_dict['ID']).first()
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
                        update_str.append(
                            f"[{obj.id}] 支付时间由 [{obj.payment_time}] 修改为 [{update_payment_time}]")

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
                log_except, title=f"作品管理批量状态维护 x-admin {sheet} 状态数据存储异常 ", e=e,
                other={"row_dict": row_dict},
                tag=["x-admin导入功能", "作品管理批量状态维护异常"],
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


@register(CaseWorksState)
class CaseWorksStateAdmin(object):
    list_display = ['title', 'order']


@register(Case)
class CaseAdmin(object):
    list_display = ['id', 'author_name', 'get_province', 'phone', 'category',
                    'level', 'state', 'payment_time', 'payment_amount', 'is_push', 'created_at']
    list_filter = ['state', 'payment_time', 'payment_amount', 'is_push', 'level', 'created_at']
    search_fields = ['title', 'phone', 'author__name', 'hospital']
    list_exclude = ["hospital", ]
    style_fields = {
        'metrics': 'preview',
    }
    list_editable = ['is_push']

    @short_description('作者姓名')
    def author_name(self, instance):
        return instance.author.name if instance.author_id else "未填写"

    @short_description("省份")
    def get_province(self, obj):
        return (obj.author.province or '-') if obj.author_id else "未填写"

    # @short_description("大区")
    # def get_region(self, obj):
    #     return (obj.author.region or "-") if obj.author_id else "未填写"
    #
    # @short_description("片区")
    # def get_precinct(self, obj):
    #     return (obj.author.precinct or '-') if obj.author_id else "未填写"

    def queryset(self):
        _queryset = super().queryset()
        return _queryset.select_related('author', 'level', 'state', )

    import_excel = True
    excel_template_uri = 'https://rcmyhg-qn.yuemia.com/media/1727417208913/病例征集批量状态维护-template-v1.xlsx'

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            excel_data = request.FILES['excel']
            current_uri = request.build_absolute_uri()
            location = settings.PRIVATE_UPLOAD_FILE_ROOT / 'case_history'

            try:
                django_storage_save(location=location, name=excel_data.name, file=excel_data)
            except Exception as e:
                fmt_error(
                    log_except, title=f"病例征集批量状态维护 x-admin 界面存储文件异常, {current_uri}", e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "病例征集批量状态维护"],
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
                "func": parse_case_history_import_func,
                "dtype": {"ID": int, "状态": str, '劳务费档位': str, '支付时间': str, '支付金额': float},
            }
            #
            sheet = "病例征集批量状态维护"
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
                    log_except, title=f"病例征集批量状态维护 x-admin {sheet} 数据存储写入异常, {current_uri}",
                    e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "病例征集批量状态维护"],
                    request=request
                )
                messages.add_message(
                    request, messages.ERROR,
                    f"SHEET {sheet} 导入存储写入异常:{e}"
                )
                return HttpResponseRedirect(current_uri)

        return super().post(request, *args, **kwargs)


def parse_case_history_import_func(
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
    state_query = CaseWorksState.objects.values("id", "title")
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
                obj = opts.default_manager.filter(id=row_dict['ID']).first()
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
                        update_str.append(
                            f"[{obj.id}] 支付时间由 [{obj.payment_time}] 修改为 [{update_payment_time}]")

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
                log_except, title=f"病例征集批量状态维护维护 x-admin {sheet} 状态数据存储异常 ", e=e,
                other={"row_dict": row_dict},
                tag=["x-admin导入功能", "病例征集批量状态维护异常"],
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


@register(MedCase)
class MedCaseAdmin(object):
    list_display = ['id', 'author_name', 'get_province', 'get_phone',
                    'disease', 'level', 'state', 'payment_time', 'payment_amount', 'is_push', 'created_at']
    list_filter = ['state', 'payment_time', 'payment_amount', 'is_push', 'level', 'created_at']
    search_fields = ['author__name', 'author__phone', 'disease__title']
    # list_exclude = ["hospital", ]
    style_fields = {
        'metrics': 'preview',
    }
    list_editable = ['is_push']
    change_form_template = "work_model_form.html"

    def has_add_permission(self, request=None, obj=None):
        return False

    def has_delete_permission(self, request=None, obj=None):
        return False

    # @short_description('医院')
    # def author_hospital(self, instance):
    #     return instance.author.hospital if instance.author_id else "未填写"

    @short_description('作者姓名')
    def author_name(self, instance):
        return instance.author.name if instance.author_id else "未填写"

    @short_description("省份")
    def get_province(self, obj):
        return (obj.author.province or '-') if obj.author_id else "未填写"

    # @short_description("大区")
    # def get_region(self, obj):
    #     return (obj.author.region or "-") if obj.author_id else "未填写"
    #
    # @short_description("片区")
    # def get_precinct(self, obj):
    #     return (obj.author.precinct or '-') if obj.author_id else "未填写"

    @short_description("手机号")
    def get_phone(self, obj):
        return (obj.author.phone or '-') if obj.author_id else "未填写"

    def queryset(self):
        _queryset = super().queryset()
        return _queryset.select_related('author', 'level', 'state', )

    def get_context(self):
        context = super().get_context()
        if hasattr(self, 'org_obj'):
            __data = self.org_obj.data
            if __data:
                for item in __data: item['kind'] = QuestionKindChoices(item['kind']).label
            context.update({
                "commit_log_json": __data
            })
        return context

    def get_form_layout(self):
        if self.org_obj:
            self.form_layout = (
                Main(
                    Fieldset(
                        '',
                        'author', 'disease', 'phone', 'level', 'state', 'payment_time', 'payment_amount',
                        'is_push',
                        css_class='unsort no_title'
                    ),

                ),

            )
        return super().get_form_layout()

    import_excel = True
    excel_template_uri = 'https://rcmyhg-qn.yuemia.com/media/1727417208913/病例征集批量状态维护-template-v1.xlsx'

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            excel_data = request.FILES['excel']
            current_uri = request.build_absolute_uri()
            location = settings.PRIVATE_UPLOAD_FILE_ROOT / 'medcase_history'

            try:
                django_storage_save(location=location, name=excel_data.name, file=excel_data)
            except Exception as e:
                fmt_error(
                    log_except, title=f"病例征集批量状态维护 x-admin 界面存储文件异常, {current_uri}", e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "病例征集批量状态维护"],
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
                "func": parse_case_history_import_func,
                "dtype": {"ID": int, "状态": str, '劳务费档位': str, '支付时间': str, '支付金额': float},
            }
            #
            sheet = "病例征集批量状态维护"
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
                    log_except, title=f"病例征集批量状态维护 x-admin {sheet} 数据存储写入异常, {current_uri}",
                    e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "病例征集批量状态维护"],
                    request=request
                )
                messages.add_message(
                    request, messages.ERROR,
                    f"SHEET {sheet} 导入存储写入异常:{e}"
                )
                return HttpResponseRedirect(current_uri)

        return super().post(request, *args, **kwargs)


@register(Disease)
class DiseaseAdmin(object):
    list_display = ['title', 'desc', 'is_use', 'order', 'created_at']
    list_filter = ['is_use', 'created_at']
    search_fields = ['title', 'desc']
    style_fields = {
        'body': 'ueditor',
        "questions": "m2m_transfer"
    }


class ItemInline(object):
    model = Item
    extra = 0


@register(Question)
class QuestionAdmin(object):
    list_display = ['kind', 'title', 'is_use', 'order', 'required', 'created_at']
    list_filter = ['is_use', 'created_at']
    search_fields = ['title']
    inlines = [ItemInline, ]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import pandas
from django.conf import settings
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from pandas import DataFrame

from user.models import Doctor
from vendor.abnormal.fmt_log_exception import fmt_error
from vendor.storage.local_storage.file import django_storage_save
from vendor.wechat.official_account import WeChatUserInfo
from xadmin.sites import register, short_description
import logging

log_except = logging.getLogger('except')


@register(Doctor)
class DoctorAdmin(object):
    list_display = ['id', 'openid', 'phone', 'name', 'province', 'state',
                    'bank', 'bank_operation_name', 'get_mask_bank_card_number', 'get_mask_card_number', 'get_sign_img_display', 'created_at']
    list_filter = ['state', 'last_login', 'is_subscribe', 'created_at']
    search_fields = ['phone', 'openid', 'name']
    readonly_fields = ['get_sign_img_display']
    style_fields = {
        'pic': 'preview',
        'sign_img': 'textarea',
    }
    list_exclude = ["hospital", 'region', 'precinct', ]
    ordering = ['custom_state']

    def queryset(self):
        _queryset = super().queryset().annotate(
            custom_state=Case(
                When(state="1", then=Value(1)),
                When(state="3", then=Value(2)),
                When(state="2", then=Value(3)),
                When(state="0", then=Value(4)),
                default=Value(4),
                output_field=IntegerField()
            )
        ).order_by('custom_state')
        return _queryset

    @short_description("银行卡号")
    def get_mask_bank_card_number(self, obj):
        if obj.bank_card_number is None:
            return ''
        return f"{obj.bank_card_number[:6]}{'*' * (len(obj.bank_card_number) - 10)}{obj.bank_card_number[-4:]}" if obj.bank_card_number and len(
            obj.bank_card_number) >= 12 else "****************"

    @short_description("身份证号码")
    def get_mask_card_number(self, obj):
        if obj.card_number is None:
            return ''
        return f"{obj.card_number[:6]}{'*' * (len(obj.card_number) - 10)}{obj.card_number[-4:]}" if obj.card_number and len(
            obj.card_number) >= 18 else "******************"

    @short_description("签名图片")
    def get_sign_img_display(self, obj):
        if obj.sign_img:
            return mark_safe(f'<img src="{obj.sign_img}" style="max-width: 200px; max-height: 100px; border: 1px solid #ddd;" />')
        return "无签名图片"

    def save_models(self):
        if self.org_obj is not None and 'state' in self.form_obj.changed_data:
            is_subscribe = self.new_obj.is_subscribe
            if not is_subscribe and self.new_obj.openid:
                is_subscribe = WeChatUserInfo.get_user_subscribe_status(self.new_obj.openid)
                if self.new_obj.is_subscribe != is_subscribe:
                    self.new_obj.is_subscribe = is_subscribe

            if is_subscribe and self.new_obj.openid:
                if 2 <= self.new_obj.state <= 3:
                    # 认证通过/认证不通过 => 推送模板消息
                    WeChatUserInfo.send_template_msg(
                        tempid=settings.TEMPLATE_ID,
                        openids=[self.new_obj.openid],
                        username=self.new_obj.name,
                        state='认证通过' if self.new_obj.state == 2 else '认证不通过',
                        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        url=f'{self.request._current_scheme_host}/mobile/register'
                    )

        return super().save_models()

    import_excel = True
    excel_template_uri = 'https://rcmyhg-qn.yuemia.com/media/1712732653033/医生白名单信息-20240410-template-01.xlsx'

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            excel_data = request.FILES['excel']
            current_uri = request.build_absolute_uri()

            try:
                django_storage_save(location=settings.PRIVATE_UPLOAD_FILE_ROOT, name=excel_data.name, file=excel_data)
            except Exception as e:
                fmt_error(
                    log_except, title=f"用户导入体系 x-admin 界面存储文件异常, {current_uri}", e=e,
                    other={"filename": excel_data.name},
                    tag=["x-admin导入功能", "医生管理导入"],
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
                "func": doctor_parse_import_func,
                "fields": ["序号", "医生姓名（必填）", "省份", "大区", "片区", "所属医院", "身份证号码",
                           "有效手机号码（必填：身份唯一标识，务必与后期注册手机号码保持一致）",
                           "银行", "银行卡号", "开户行名称"],
                "dtype": {"序号": str, "医生姓名（必填）": str, "省份": str, "大区": str, "片区": str,
                          "所属医院": str, "身份证号码": str,
                          "有效手机号码（必填：身份唯一标识，务必与后期注册手机号码保持一致）": str, "银行": str,
                          "银行卡号": str, "开户行名称": str, },
            }
            for sheet in sheet_names:
                data = excel_reader.parse(sheet_name=sheet, dtype=records['dtype'])
                data.replace('空', '', inplace=True)
                shape_ = data.shape[0]
                template_head_ = data.columns.tolist()
                if shape_ == 0 or template_head_ != records['fields']:
                    messages.add_message(
                        request, messages.ERROR,
                        f"SHEET {sheet} 表头格式不规范; {template_head_}, 正确表头字段：{records['fields']}"
                    )
                    return HttpResponseRedirect(current_uri)

                # validate db
                try:
                    with atomic():
                        records['func'](data, shape_, sheet, request)
                except Exception as e:
                    fmt_error(
                        log_except, title=f"用户导入体系 x-admin {sheet} 数据存储异常, {current_uri}", e=e,
                        other={"filename": excel_data.name},
                        tag=["x-admin导入功能", "医生管理导入"],
                        request=request
                    )
                    messages.add_message(
                        request, messages.ERROR,
                        f"SHEET {sheet} 导入存储异常:{e}"
                    )
                    return HttpResponseRedirect(current_uri)

        return super().post(request, *args, **kwargs)


def doctor_parse_import_func(
        data: DataFrame,
        shape: int,
        sheet: str,
        request
):
    row_count = data.shape[0]
    doctors = []
    Repeat_phone = []

    required_cols = [col for col in data.columns if '（必填）' in col]
    # 过滤掉在这些列中任一列值为空的行
    data.dropna(subset=required_cols, inplace=True)

    phones = data['有效手机号码（必填：身份唯一标识，务必与后期注册手机号码保持一致）'].tolist()
    phone_set = {
        x['phone']: True for x in Doctor.objects.filter(phone__in=phones).values("phone")
    } if len(phones) > 0 else {}

    comm_str = f"SHEET {sheet} 共计读取{row_count}条数据，过滤有效数据{data.shape[0]}条，"
    for index, row in data.fillna("").iterrows():
        row_dict = row.to_dict()
        _phone = row_dict.get('有效手机号码（必填：身份唯一标识，务必与后期注册手机号码保持一致）')
        if phone_set.get(_phone) is True:
            Repeat_phone.append(_phone)
        else:
            doctors.append(
                Doctor(
                    phone=_phone, name=row_dict.get('医生姓名（必填）'), hospital=row_dict.get('所属医院'),
                    province=row_dict.get('省份'), region=row_dict.get('大区'), precinct=row_dict.get('片区'),
                    bank=row_dict.get('银行'), bank_card_number=row_dict.get('银行卡号'),
                    card_number=row_dict.get('身份证号码'), bank_operation_name=row_dict.get('开户行名称')
                )
            )

        # row_dict = {
        # '序号': 'YM00010',
        # '医生姓名（必填）': '',
        # '省份': '',
        # '大区': '',
        # '片区': '',
        # '所属医院': '',
        # '有效手机号码（必填：身份唯一标识，务必与后期注册手机号码保持一致）': ''
        # }
        # print(f"row_dict={row_dict}")
    if len(doctors) > 0:
        objs = Doctor.objects.bulk_create(doctors)
        comm_str += f"成功写入医生数据{len(objs)}条。"
    else:
        comm_str += "未检测到有效医生数据。"
    repeat_phone_len = len(Repeat_phone)
    if repeat_phone_len > 0:
        comm_str += f"检测到重复手机号码{repeat_phone_len}条，手机号码：{','.join(Repeat_phone)}, 以上数据不会入库存储。"

    messages.add_message(
        request, messages.SUCCESS,
        comm_str
    )

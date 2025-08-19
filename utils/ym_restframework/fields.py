#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class DisplayChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        """返回选项的值"""
        return self._choices[obj]


class DisplayDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        value = super().to_representation(value)
        if value:
            value = value.format(y="年", m="月", d="日", h="时", f="分", s="秒")
        return value


class HideCharField(serializers.CharField):
    """字段脱敏"""

    default_error_messages = {
        "invalid": _("Not a valid string."),
        "blank": _("This field may not be blank."),
        "max_length": _("Ensure this field has no more than {max_length} characters."),
        "min_length": _("Ensure this field has at least {min_length} characters."),
        "num_length": _("front_num or after_num or star_num must greater than 0"),
    }

    def __init__(self, **kwargs):
        self.front_num = kwargs.pop("front_num", 3)  # 保留前n位
        self.after_num = kwargs.pop("after_num", 4)  # 保留后n位
        self.star_num = kwargs.pop("star_num", 4)  # 星的位数
        self.is_all_hide = kwargs.pop("is_all_hide", False)  # 全脱敏
        self.is_hide = kwargs.pop("is_hide", True)  # 是否需要有脱敏

        self.hide_str = "*" * self.star_num

        if self.front_num < 0 or self.after_num < 0 or self.star_num <= 0:
            self.fail("num_length")

        super().__init__(**kwargs)

    def to_representation(self, value):
        value = super().to_representation(value)

        if not self.is_hide:
            return value

        if value and self.is_all_hide:
            return self.hide_str

        if value:
            front_str = ""
            after_str = ""
            if self.front_num != 0 and len(value) > self.front_num:
                front_str = value[: self.front_num]
            if self.after_num != 0 and len(value) > self.after_num:
                after_str = value[-self.after_num :]
            return f"{front_str}{self.hide_str}{after_str}"

        return value


class PhoneCharField(HideCharField):
    def __init__(self, **kwargs):
        self.is_validate = kwargs.pop("is_validate", True)  # 是否需有校验
        super().__init__(front_num=3, after_num=4, star_num=4, **kwargs)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if not data:
            return data
        if not self.is_validate:
            return data
        data = re.match(r"^1[35678]\d{9}$", data)
        if not data:
            self.fail("invalid")
        return data.string

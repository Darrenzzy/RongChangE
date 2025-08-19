#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import traceback

from django.db.utils import IntegrityError
from rest_framework.serializers import IntegerField, ValidationError

from .exceptions import TextError


def validate(self, attrs, *args, **kwargs):
    """
    rest_framework.Serializer.validate
    args, kwargs 是通过装饰器扩展的参数
    """
    funcs = kwargs.get("funcs", [])
    for func in funcs:
        attrs = func(self, attrs)
    return attrs


class ForeignKeyField(IntegerField):
    def __init__(self, model_class=None, **kwargs):
        if not model_class:
            raise ValidationError("model_class not found")
        self.model_class = model_class
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        exists = self.model_class.objects.filter(id=data).exists()
        if not exists:
            raise ValidationError(f"{data} not found")
        return super().to_internal_value(data)


class SerializerCreate:
    def create(self, validated_data):
        ModelClass = self.Meta.model
        try:
            instance = ModelClass._default_manager.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                "Got a `TypeError` when calling `%s.%s.create()`. "
                "This may be because you have a writable field on the "
                "serializer class that is not a valid argument to "
                "`%s.%s.create()`. You may need to make the field "
                "read-only, or override the %s.create() method to handle "
                "this correctly.\nOriginal exception was:\n %s"
                % (
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    self.__class__.__name__,
                    tb,
                )
            )
            raise TypeError(msg)
        except IntegrityError as exc:
            err_code, err_msg, *_ = exc.args
            pattern = "[^(Duplicate entry ')](\d)+[^(' for key ')]"
            repetitive_value = re.search(pattern, str(err_msg))
            if repetitive_value:
                raise TextError(f"{repetitive_value.group()}已存在")
            raise TextError("请勿重复创建")
        return instance


class SerializerUpdate:
    def update(self, instance, validated_data):
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            instance.refresh_from_db()
        except IntegrityError as exc:
            err_code, err_msg, *_ = exc.args
            pattern = "[^(Duplicate entry ')](\d)+[^(' for key ')]"
            repetitive_value = re.search(pattern, str(err_msg))
            if repetitive_value:
                raise TextError(f"{repetitive_value.group()}已存在")
            raise exc
        return instance

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

from .utils import get_class

logger = logging.getLogger(__name__)


def get_ym_serializer_classes(self):
    assert getattr(self, "ym_serializer_classes", None), (
        "'%s' 应该包含 `ym_serializer_classes` 字段配置，"
        "或者重写 `get_ym_serializer_classes` 方法." % self.__class__.__name__
    )
    return self.ym_serializer_classes


def get_serializer_class(self):
    """
    generic.GenericAPIView
    """
    if hasattr(self, "ym_serializer_classes"):
        ym_serializer_classes = self.get_ym_serializer_classes()
        serializer_class = get_class(self.action, ym_serializer_classes)

        if serializer_class:
            return serializer_class
        raise Exception(f"{self.__class__.__name__}.ym_serializer_classes 配置有误")

    # 不存在 serializer_classes， 则使用 serializer_class
    assert self.serializer_class is not None, (
        "'%s' should either include a `serializer_class` attribute, "
        "or override the `get_serializer_class()` method." % self.__class__.__name__
    )

    return self.serializer_class

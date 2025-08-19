#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException, _get_error_details
from django.utils.translation import gettext_lazy as _

from .status import (
    HTTP_4450_CUSTOM_TEXT,
    HTTP_4500_INTERNAL_SERVER_ERROR,
    BaseHttpStatus,
)


class TextValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        # self.detail = ",".join([str(x) for x in _get_error_details(detail, code)])
        self.detail = " ".join(_get_error_details(detail, code))


class StatusError(Exception):
    """抛出指定 status_class 的异常"""

    default_status_class = HTTP_4500_INTERNAL_SERVER_ERROR

    def __init__(self, status_class, *args, **kwargs):
        """kwargs中的参数，用于格式化status_code中的message"""

        assert issubclass(
            status_class, BaseHttpStatus
        ), f'{status_class.__name__} must be subclass of "BaseHttpStatus"'

        self.status = status_class.status
        self.message = status_class.message

        if args or kwargs:
            self.message = self.message.format(*args, **kwargs)


class TextError(Exception):
    """抛出指定text的异常；status固定， 一般用于client展示方案"""

    default_status_class = HTTP_4450_CUSTOM_TEXT

    def __init__(self, text: str, *args, **kwargs):

        assert text, '"TextError" text is required'

        status_class = self.default_status_class
        self.status = status_class.status
        self.message = text

        if args or kwargs:
            self.message = self.message.format(*args, **kwargs)

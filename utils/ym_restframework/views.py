#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

from django.http import Http404
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import set_rollback

from .exceptions import StatusError, TextError
from .status import (
    HTTP_4429_TOO_MANY_REQUESTS,
    HTTP_4500_INTERNAL_SERVER_ERROR,
    get_status_class,
)
from .utils import get_class, get_response_data

logger = logging.getLogger(__name__)


def get_ym_authentication_classes(self):
    assert hasattr(self, "ym_authentication_classes"), (
        "'%s' 应该包含 `ym_authentication_classes` 字段配置，"
        "或者重写 `get_ym_authentication_classes` 方法." % self.__class__.__name__
    )
    return self.ym_authentication_classes


def get_authenticators(self):
    """
    Instantiates and returns the list of authenticators that this view can use.
    """
    if hasattr(self, "ym_authentication_classes"):
        ym_authentication_classes = self.get_ym_authentication_classes()
        authentication_classes = get_class(self.action, ym_authentication_classes)
        if authentication_classes is None:
            raise Exception(f"{self.__class__.__name__}.ym_authentication_classes 配置有误")
    else:
        authentication_classes = self.authentication_classes
    return [auth() for auth in authentication_classes]


def get_ym_permission_classes(self):
    assert hasattr(self, "ym_permission_classes"), (
        "'%s' 应该包含 `ym_permission_classes` 字段配置，"
        "或者重写 `get_ym_permission_classes` 方法." % self.__class__.__name__
    )
    return self.ym_permission_classes


def get_permissions(self):
    """
    Instantiates and returns the list of permissions that this view requires.
    """
    if hasattr(self, "ym_permission_classes"):
        ym_permission_classes = self.get_ym_permission_classes()
        permission_classes = get_class(self.action, ym_permission_classes)
        if permission_classes is None:
            permission_classes = self.permission_classes
    else:
        permission_classes = self.permission_classes
    return [permission() for permission in permission_classes]


def get_ym_throttle_classes(self):
    assert hasattr(self, "ym_throttle_classes"), (
        "'%s' 应该包含 `ym_throttle_classes` 字段配置，"
        "或者重写 `get_ym_throttle_classes` 方法." % self.__class__.__name__
    )
    return self.ym_throttle_classes


def get_throttles(self):
    """
    Instantiates and returns the list of throttles that this view uses.
    """
    if hasattr(self, "ym_throttle_classes"):
        ym_throttle_classes = self.get_ym_throttle_classes()
        throttle_classes = get_class(self.action, ym_throttle_classes)
        if throttle_classes is None:
            throttle_classes = self.throttle_classes
    else:
        throttle_classes = self.throttle_classes
    return [throttle() for throttle in throttle_classes]


def throttled(self, request, wait):
    """
    If request is throttled, determine what kind of exception to raise.
    """
    raise StatusError(HTTP_4429_TOO_MANY_REQUESTS)


def get_msg_from_response(data, err_field=None):
    """从response中取出返回值文案"""
    if not data:
        return

    if isinstance(data, dict):
        dict_key, dict_value = list(data.items())[0]
        if isinstance(dict_value, str):
            if dict_key == "detail":
                return dict_value
            return f"`{dict_key}` {dict_value}"
        return get_msg_from_response(dict_value, err_field=dict_key)

    if isinstance(data, list):
        first_value = data[0]
        if isinstance(first_value, str):
            if err_field:
                return f"`{err_field}` {first_value}"
        return get_msg_from_response(first_value)

    return data


# 不是 rest 预期的异常处理，
# 原逻辑是直接报 500，这里简单处理一下，返回 client 正常数据
# ---
# 还有另外一种处理方式
# 自定义settings.EXCEPTION_HANDLER变量，此变量默认指向 rest_framework.views.exception_handler方式
# 继承 rest_framework.views.exception_handler 后添加自己的异常处理方式
# 不过要配置变量到settings中，容易被遗忘，没有下面方式方面


# raise_uncaught_exception返回值处理
def handle_exception(self, exc):
    """
    views.APIView
    """
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        # WWW-Authenticate header for 401 responses, else coerce to 403
        auth_header = self.get_authenticate_header(self.request)

        if auth_header:
            exc.auth_header = auth_header
        else:
            exc.status_code = HTTP_403_FORBIDDEN

    exception_handler = self.get_exception_handler()

    context = self.get_exception_handler_context()
    response = exception_handler(exc, context)

    if response:
        # restframework预期异常，处理成固定格式
        StatusClass = get_status_class(response.status_code)
        response.status_code = HTTP_200_OK
        response.data = get_response_data(
            StatusClass.status,
            get_msg_from_response(response.data) or StatusClass.message,
        )
    else:
        # StatusError、TextError异常，处理成固定格式
        if isinstance(exc, (StatusError, TextError)):
            response = Response(get_response_data(exc.status, exc.message))
        else:
            # 非预期异常，处理成固定格式，并打印日志
            _logger = getattr(exc, "logger", None) or logger
            _logger.exception("\n")
            StatusClass = get_status_class(HTTP_500_INTERNAL_SERVER_ERROR)
            response = Response(
                get_response_data(
                    StatusClass.status,
                    str(exc) or StatusClass.message,
                )
            )

    response.exception = True
    return response


def dispatch(self, request, *args, **kwargs):
    """
    views.APIView
    """

    self.args = args
    self.kwargs = kwargs

    response = None

    try:
        request = self.initialize_request(request, *args, **kwargs)
    except Exception as exc:
        _logger = getattr(exc, "logger", None) or logger
        _logger.exception("\n" * 3)
        request = request
        StatusClass = get_status_class(HTTP_500_INTERNAL_SERVER_ERROR)
        response = Response(
            get_response_data(
                StatusClass.status,
                str(exc) or StatusClass.message,
            )
        )

    self.request = request
    self.headers = self.default_response_headers  # deprecate?

    if response is None:
        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            method = request.method.lower()

            if method in ("head",):
                response = Response()
            else:
                handler = self.http_method_not_allowed
                if method in self.http_method_names:
                    handler = getattr(self, method, self.http_method_not_allowed)
                response = handler(request, *args, **kwargs)
                if not response:
                    raise StatusError(HTTP_4500_INTERNAL_SERVER_ERROR)

            if isinstance(response, Response):
                # 正常的返回值，处理成固定格式
                data = response.data
                message = None
                if isinstance(data, dict):
                    detail = data.pop("detail", None)
                    if detail:
                        message = detail
                elif isinstance(data, str):
                    message = data
                    data = None

                StatusClass = get_status_class(response.status_code)
                response.data = get_response_data(
                    StatusClass.status,
                    message or StatusClass.message,
                    data=data,
                )
                response.status_code = HTTP_200_OK
        except Exception as exc:
            response = self.handle_exception(exc)
            if not hasattr(self, "headers"):
                setattr(self, "headers", {})

    self.response = self.finalize_response(request, response, *args, **kwargs)
    return self.response


# Exception handling
# 'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
from rest_framework import exceptions
from django.core.exceptions import PermissionDenied


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound(*(exc.args))
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied(*(exc.args))

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, str):
            data = exc.detail
        elif isinstance(exc.detail, list):
            data = " ".join(exc.detail)
        elif isinstance(exc.detail, dict):
            data = " ".join([f"{k}:{','.join([str(xv) for xv in v])}" for k, v in exc.detail.items()])
        else:
            data = exc.detail

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None

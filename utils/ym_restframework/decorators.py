#!/usr/bin/env python
# -*- coding: utf-8 -*-


from functools import wraps

from . import generic, serializers, views, viewsets


def ym_api(cls):

    _dict = cls.__dict__

    # 在 get_authenticators() 之前 初始化 action
    cls.initialize_request = viewsets.initialize_request

    # 自定义 ym_serializer_classes
    cls.get_ym_serializer_classes = generic.get_ym_serializer_classes
    if "get_serializer_class" not in _dict:
        cls.get_serializer_class = generic.get_serializer_class

    # 自定义 ym_authentication_classes
    cls.get_ym_authentication_classes = views.get_ym_authentication_classes
    cls.get_authenticators = views.get_authenticators

    # 自定义 ym_permission_classes
    cls.get_ym_permission_classes = views.get_ym_permission_classes
    cls.get_permissions = views.get_permissions

    # 自定义 ym_throttle_classes
    cls.get_ym_throttle_classes = views.get_ym_throttle_classes
    cls.get_throttles = views.get_throttles
    cls.throttled = views.throttled

    # 自定义 返回数据格式
    cls.dispatch = views.dispatch
    cls.handle_exception = views.handle_exception
    return cls


def ym_add_args_kwargs(*args, **kwargs):
    """给方法增加额外的参数"""
    _args = list(args)
    _kwargs = kwargs

    def add_args_kwargs(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            args = list(args)
            args.extend(_args.copy())
            kwargs.update(_kwargs.copy())
            return func(*args, **kwargs)

        return wrapper_func

    return add_args_kwargs


def ym_validate(funcs=None):
    """通过重写def validate，增加自定义校验方法， 方法必须以 'check_' 开头"""
    if funcs is not None:
        assert isinstance(funcs, (tuple, list)), "'funcs' 必须为元组或列表对象"
        for func in funcs:
            if not func.__name__.startswith("check_"):
                raise Exception("func 必须以 'check_' 开头")

    def wrapper_cls(cls):
        if funcs is None:
            return cls
        # 把用户自定义的校验方法添加到类里面
        for func in funcs:
            setattr(cls, func.__name__, func)
        # def validate 重定义
        cls.validate = ym_add_args_kwargs(funcs=funcs)(serializers.validate)
        return cls

    return wrapper_cls


def catch_exception(logger):
    """
    捕获一个方法中的异常，并使用指定logger处理
    只要在 @ym_api() 修饰的viewset中才会生效
    原因：与ym_views.raise_uncaught_exception配合使用
    """

    def try_except(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                exc.logger = logger
                raise exc

        return wrapper_func

    return try_except

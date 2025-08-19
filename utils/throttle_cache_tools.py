#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: throttle_cache_tools.py

@author: 'ovan'

@mtime: '2024/7/19'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import typing

from django.core.cache import caches


def check_throttle_limit_range(
        throttle_key: typing.List[str],
        throttle_top: typing.List[int],
        timeout: typing.List[int],
        cache_slots: str = 'default',
) -> (bool, typing.List[str]):
    """
    检查是否在频率限制范围内
    :param throttle_key: 频率限制的key
    :param throttle_top: 频率限制的上限
    :param timeout: 频率限制的超时时间
    :param cache_slots: 缓存槽位
    :return: True/False  是否需要等待
    """

    if len({len(throttle_key), len(throttle_top), len(timeout)}) != 1:
        raise ValueError('throttle_key, throttle_top and timeout must be the same length')

    is_wait = False  # 是否触发速率规则限制
    wait_throttle = []  # 触发的规则key

    for index, _throttle_key in enumerate(throttle_key):
        _throttle_top = throttle_top[index]
        _timeout = timeout[index]

        def incr_throttle_callable():
            """
            请在业务结束后调用该方法，以便缓存计数
            """
            caches[cache_slots].incr(_throttle_key) \
                if caches[cache_slots].has_key(_throttle_key) \
                else caches[cache_slots].set(_throttle_key, 1, timeout=_timeout)

        key_is_exists = caches[cache_slots].get(_throttle_key)
        if key_is_exists:
            # 是否到达阈值
            if key_is_exists >= _throttle_top:
                is_wait = True
                wait_throttle.append(_throttle_key)
            else:
                incr_throttle_callable()
        else:
            incr_throttle_callable()

    return is_wait, wait_throttle


def get_ip_address(request):
    try:
        ip_addr = request.META['HTTP_X_FORWARDED_FOR'] if request.META[
            'HTTP_X_FORWARDED_FOR'] else \
            request.META['REMOTE_ADDR']
    except KeyError:
        ip_addr = request.META.get('REMOTE_ADDR')
    return ip_addr

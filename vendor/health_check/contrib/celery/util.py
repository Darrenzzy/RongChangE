#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: de.py

@author: 'ovan'

@mtime: '2024/8/20'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import signal


# 定义一个自定义的异常，用于超时信号
class TimeoutException(Exception):
    pass


# 定义一个装饰器，用于设置函数执行的超时时间
def timeout_control(seconds: int = 1, error_message: str = "Function call timed out"):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutException(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # 确保信号处理函数被清除
            return result

        return wrapper

    return decorator

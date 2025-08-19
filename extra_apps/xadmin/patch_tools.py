#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: patch_tools.py

@author: 'ovan'

@mtime: '2023/4/20'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from functools import wraps
from django.utils.cache import add_never_cache_headers


def never_cache(view_func):
    """
    Decorator that adds headers to a response so that it will never be cached.
    """

    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response

    return _wrapped_view_func

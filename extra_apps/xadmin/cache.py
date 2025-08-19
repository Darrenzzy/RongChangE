#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: cache.py

@author: 'ovan'

@mtime: '2023/4/24'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from django.conf import settings
from django.core.cache import caches


def get_default_cache():
    """
    获取默认的cache
    """
    # https://docs.djangoproject.com/zh-hans/4.2/ref/settings/#caches
    local_cache = settings.CACHES.get("default", None)
    if local_cache is None:
        settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
    return caches['default']

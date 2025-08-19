#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: views.py

@author: 'ovan'

@mtime: '2024/8/19'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from django.conf import settings
from django.core.cache import caches
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from vendor.health_check.cache.backends import CacheBackend
# from vendor.health_check.contrib.celery.backends import CeleryHealthCheck
# from vendor.health_check.contrib.celery_ping.backends import CeleryPingHealthCheck
from vendor.health_check.contrib.db.backends import DatabaseBackend

check_list = [
    CacheBackend,
    DatabaseBackend,
    # CeleryHealthCheck,
    # CeleryPingHealthCheck,
]

cache_key = 'health_check_status_cache'


def get_default_cache(cache_name: str = 'default'):
    """
    获取默认的cache
    """
    # https://docs.djangoproject.com/zh-hans/4.2/ref/settings/#caches
    local_cache = settings.CACHES.get(cache_name, None)
    if local_cache is None:
        settings.CACHES[cache_name] = {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',  # 这个值可以是任何字符串，用于区分不同的 LocMemCache 实例
        }
    return caches[cache_name]


def healthcheck(request):
    project_name = request.META.get("HTTP_PROJECT_NAME", '')
    application_name = getattr(settings, 'ASGI_APPLICATION') or settings.WSGI_APPLICATION
    if project_name != application_name:
        return Response(
            {"message": "project_name error."},
            status=400
        )

    result = get_default_cache().get(cache_key)
    if result:
        # {"content": {...}, "status": 200}
        return JsonResponse(result.get("content", {}), status=result.get("status", 200))

    code = 200
    errors = {}
    for backend in check_list:
        backend_instance = backend()
        backend_instance.check_status()
        errors[backend_instance.identifier()] = backend_instance.pretty_status()
        if backend_instance.errors and code == 200:
            code = 400

    # successful=5min， other=2min
    get_default_cache().set(cache_key, {"content": errors, "status": code}, timeout=300 if code == 200 else 120)
    return JsonResponse(errors, status=code)


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        project_name = request.META.get("HTTP_PROJECT_NAME", '')
        application_name = getattr(settings, 'ASGI_APPLICATION') or settings.WSGI_APPLICATION
        if project_name != application_name:
            return Response(
                {"message": "project_name error."},
                status=400
            )

        try:
            result = get_default_cache().get(cache_key)
            if result:
                # {"content": {...}, "status": 200}
                return Response(result.get("content", {}), status=result.get("status", 200))
        except:
            pass

        code = 200
        errors = {}
        for backend in check_list:
            backend_instance = backend()
            backend_instance.check_status()
            errors[backend_instance.identifier()] = backend_instance.pretty_status()
            if backend_instance.errors and code == 200:
                code = 400

        try:
            # successful=5min， other=2min
            get_default_cache().set(cache_key, {"content": errors, "status": code}, timeout=300 if code == 200 else 120)
        except:
            pass
        return Response(errors, status=code)

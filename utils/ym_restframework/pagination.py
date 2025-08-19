#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import random
from collections import OrderedDict

import six
from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination, _positive_int
from rest_framework.settings import api_settings
from rest_framework.utils.urls import replace_query_param as replace_query_param_

from .urls import remove_query_param, replace_query_param


class BasePagination(PageNumberPagination):
    """
    上一页、下一页处理成相对路径
    """

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()

        if hasattr(self, "_reset_query_params"):
            for key, value in self._reset_query_params.items():
                url = replace_query_param_(url, key, value)

        page_number = self.page.next_page_number()
        _next_link = replace_query_param(url, self.page_query_param, page_number)
        return _next_link

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()

        if hasattr(self, "_reset_query_params"):
            for key, value in self._reset_query_params.items():
                url = replace_query_param_(url, key, value)

        page_number = self.page.previous_page_number()

        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def reset_query_params(self, data=None):
        """
        重置request.query_params上面的参数
        原理：在用到request.query_params时，查询一次当前的_reset_query_params里面的值
        """
        if data is None:
            data = {}
        self._reset_query_params = data

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("count", self.page.paginator.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_page_size(self, request):
        if self.page_size_query_param:

            if (
                    hasattr(self, "_reset_query_params")
                    and self.page_size_query_param in self._reset_query_params
            ):
                return self._reset_query_params[self.page_size_query_param]

            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size,
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)

        # 重置查询的页码
        if hasattr(self, "_reset_query_params"):
            page_number = self._reset_query_params.get(
                self.page_query_param, page_number
            )

        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)


class YmPageNumberPagination(BasePagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 2000


class RandomPageNumberPagination(BasePagination):
    """
    http://api.example.org/accounts/?page_timestamp=1234567890123&page=4
    http://api.example.org/accounts/?page_timestamp=1234567890123&page=4&page_size=100
    需求：数据分页展示, 排序是随机的
    实现：
    - 首先 settings 中要有 redis 的配置， 默认为 default
    - 获取到要分页的 queryset
    - 判断是否有时间戳 page_timestamp 字段
        - 如果没有的话，执行默认分页逻辑 CommonPageNumberPagination
        - 如果有 timestamp 的话，判断缓存中是否存在 value
            - 如果缓存中存在 value 直接取出做为 id_list
            - 没有缓存中不存在， 取 queryset 前 1000 条数据的 id 打乱做为 id_list，以 timestamp 为 key 存入 redis 取存入缓存中
    - 以 id_list 做数据集，执行分页
    - 取出对应一页的 id_list ， 查询 queryset 集
    - 返回数据
    """

    max_page_size = 50
    page_timestamp_timeout = getattr(settings, "PAGE_TIMESTAMP_TIMEOUT", 3600)
    page_timestamp_query_param = "page_timestamp"
    page_size_query_param = "page_size"
    cache_key = None

    def get_cache_key(self):
        _cache_key = "default"

        if self.cache_key:
            _cache_key = self.cache_key

        elif hasattr(api_settings, "cache_key"):
            _cache_key = getattr(api_settings, "cache_key")

        if _cache_key not in settings.CACHES:
            raise InvalidCacheBackendError(
                "Could not find config for '%s' in settings.CACHES" % _cache_key
            )

        return _cache_key

    def get_page_timestamp(self, request):
        """从 request 中获取时间戳字段"""
        if self.page_timestamp_query_param:
            _page_timestamp = request.query_params.get(
                self.page_timestamp_query_param, None
            )
            if _page_timestamp:
                return f"page_timestamp_{_page_timestamp}"

    def get_cache(self):
        """获取 cache"""
        return caches[self.get_cache_key()]

    def get_model_class(self, queryset):
        _first = queryset.first()
        assert _first, "queryset is not empty"
        return _first.__class__

    def paginate_queryset(self, queryset, request, view=None):
        """分页逻辑"""
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        origin_queryset = queryset
        queryset_is_id_list = False
        # 判断是否有时间戳
        page_timestamp = self.get_page_timestamp(request)
        if page_timestamp:

            # 查询 id_list
            cache = self.get_cache()
            id_list = cache.get(page_timestamp)

            # id_list 不存在，则创建
            if id_list:
                cache.expire(page_timestamp, timeout=self.page_timestamp_timeout)
                queryset = json.loads(id_list)
                queryset_is_id_list = True

            elif queryset:
                # 从queryset中随机取 2000 条数据的 id
                # 这个方法，在数据表中数据量过大时，速度慢，在表数据量过大时，可能会导致线上mysql崩溃
                queryset = queryset.order_by("?")[:2000]
                id_list = list(queryset.values_list("id", flat=True))
                random.shuffle(id_list)  # 2000 数据，再次打乱
                # 设置缓存， 过期时间是 3600s
                cache.set(
                    page_timestamp,
                    json.dumps(id_list),
                    timeout=self.page_timestamp_timeout,
                )
                queryset = id_list
                queryset_is_id_list = True

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request

        # queryset 是id_list， 分页处理后，就是一页的 id_list 数据， 转化志 Queryset 对象
        if page_timestamp and queryset_is_id_list:
            model_class = self.get_model_class(origin_queryset)
            list_page = []
            for _id in list(self.page):
                list_page.append(model_class.objects.get(id=_id))
        else:
            list_page = list(self.page)

        return list_page

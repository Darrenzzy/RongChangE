#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .pagination import YmPageNumberPagination


class OwnListModelMixin:

    own_field = "user"

    @action(["get"], detail=False)
    def own_list(self, request, *args, **kwargs):
        """查询用户自己的列表"""
        queryset = self.filter_queryset(self.get_queryset())
        user = request.user
        if user:
            queryset = queryset.filter(**{self.own_field: user})
        else:
            queryset = []

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OwnRetrieveModelMixin:
    own_field = "user"

    @action(["get"], detail=True)
    def own_retrieve(self, request, *args, **kwargs):
        """查询详情时判断是否归属用户自己"""
        user = request.user
        if user:
            instance = self.get_object()
            _user = getattr(instance, self.own_field)
            if _user.id == user.id:
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
        raise PermissionDenied()


class CommonMixin:
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = YmPageNumberPagination

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : Uyynot
# @Email    : uyynot@qq.com
# @Time     : 2024-10-30 15:39
# @File     : throttles.py
# @Project  : RongChangE
# @Desc     :
from rest_framework.throttling import UserRateThrottle


class MedCaseUserRateThrottle(UserRateThrottle):
    """病例提交视图限流类"""
    THROTTLE_RATES = {"user": "10/min"}
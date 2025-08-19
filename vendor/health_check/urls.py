#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: urls.py

@author: 'ovan'

@mtime: '2024/8/19'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from django.urls import path

from vendor.health_check.views import HealthCheckView

urlpatterns = [
    # path("health-check", healthcheck,),
    path("health-check", HealthCheckView.as_view(), ),
]

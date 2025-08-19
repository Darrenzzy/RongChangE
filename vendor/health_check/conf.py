#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: conf.py

@author: 'ovan'

@mtime: '2024/8/19'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from django.conf import settings

HEALTH_CHECK = getattr(settings, "HEALTH_CHECK", {})
HEALTH_CHECK.setdefault("DISK_USAGE_MAX", 90)  # percent
HEALTH_CHECK.setdefault("MEMORY_MIN", 100)  # in MB
HEALTH_CHECK.setdefault("WARNINGS_AS_ERRORS", True)
HEALTH_CHECK.setdefault("SUBSETS", {})
HEALTH_CHECK.setdefault("DISABLE_THREADING", False)

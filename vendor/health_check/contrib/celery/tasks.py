#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: tasks.py

@author: 'ovan'

@mtime: '2024/8/19'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from celery import shared_task


@shared_task(ignore_result=False)
def add(x: int, y: int) -> int:
    return x + y

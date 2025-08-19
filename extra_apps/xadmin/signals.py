#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: signals.py

@author: 'ovan'

@mtime: '2023/4/24'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from django.contrib.auth import user_logged_in, get_user_model, user_login_failed, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_in, sender=get_user_model())
def user_logged_in_patch(sender, request, user, **kwargs):
    print(f"user_logged_in_patch = {sender, request, user, kwargs}")
    pass


@receiver(user_login_failed, sender=get_user_model())
def user_login_failed_patch(sender, credentials, request, **kwargs):
    print(f"user_logged_in_patch = {sender, credentials, request, kwargs}")
    pass


@receiver(user_logged_out, sender=get_user_model())
def user_logged_out_patch(sender, request, user, **kwargs):
    print(f"user_logged_in_patch = {sender, request, user, kwargs}")
    pass

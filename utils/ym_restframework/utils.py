#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_class(action, ym_class, **kwargs):
    if action in ym_class:
        return ym_class[action]

    if "default" in ym_class:
        return ym_class["default"]


def get_response_data(status, message, data=None):
    return {"code": status, "msg": message, "data": data}

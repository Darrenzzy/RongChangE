#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: django_logger.py

@author: 'ovan'

@mtime: '2023/4/7'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import logging

from django.utils.timezone import now

from django.conf import settings

from utils.vendor.logger_helper.json_formatter_log import JSONFormatter


class CustomisedJSONFormatter(JSONFormatter):
    def json_record(self, message: str, extra: dict, record: logging.LogRecord):
        if not hasattr(settings, "APP_ID"):
            raise AttributeError("Please config settings APP_ID")

        context = extra
        django = {
            'app': settings.APP_ID,
            'name': record.name,
            'filename': record.filename,
            'funcName': record.funcName,
            'msecs': record.msecs,
        }
        if record.exc_info:
            django['exc_info'] = self.formatException(record.exc_info)

        return {
            'message': message,
            'timestamp': now(),
            'level': record.levelname,
            'context': context,
            'django': django
        }

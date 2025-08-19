#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: fmt_log_exception.py

@author: 'ovan'

@mtime: '2019/12/31'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import logging
import traceback
from threading import Thread

from django.conf import settings
from django.core.mail import send_mail

log_except = logging.getLogger("except")

default_filter_str = ["'", '"', "\n", "\n\r", "\r\n", ]


def fmt_error(log, title, e, other='', request=None):
    """
    提取 Log Error 错误栈

    :param log:     log instance eg: log_validate = logging.getLogger("validate")
    :param title:   log 标题
    :param e:       log 错误栈 Exception
    :param other:   log 辅助性描述
    :param request: django request 辅助性描述
    :return:
    """

    traceback_format = replace_space(default_filter_str, traceback.format_exc())
    log.error(
        {
            "error_type": replace_space(default_filter_str, f"{type(e)}"),
            "error_message": replace_space(default_filter_str, str(e)),
            "other": replace_space(default_filter_str, other),
            "title": f"{getattr(settings, 'PROJECT_NAME', 'django')}-"
                     f"{getattr(settings, 'TOP_DOMAIN', 'undefined-your-site-domain')}",
            "error_uri": f"当前请求异常路径uri={request.build_absolute_uri()}" if request is not None else "",
            "traceback": traceback_format,
        }
    )
    if settings.DEBUG:
        # print error traceback
        print("===================== START  {0},错误={1}, {2}  START =====================".format(title, e, other))
        traceback.print_exc()

    else:
        # new thread send email error log
        thr = Thread(target=core_send_mail,
                     args=(title, traceback.format_exc(), settings.DEFAULT_FROM_EMAIL, [settings.ADMINS[0][1]]))
        thr.start()


def replace_space(sep: list, source: str) -> str:
    if not source or len(sep) == 0:
        return source

    for x in sep:
        source = source.replace(x, '')
    return source


def core_send_mail(
        subject, message, from_email, recipient_list,
        fail_silently=False, auth_user=None, auth_password=None,
        connection=None, html_message=None
):
    """
    django admin email log
    """
    send_status = send_mail(
        subject, message, from_email, recipient_list,
        fail_silently, auth_user, auth_password,
        connection, html_message
    )
    log_except.info(f"core_send_mail subject={subject}, message={message}, from_email={from_email},"
                    f" recipient_list={recipient_list} 发送状态 {send_status}")

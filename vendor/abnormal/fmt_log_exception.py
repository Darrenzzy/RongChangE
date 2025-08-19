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
import uuid
from copy import copy
from threading import Thread

from django.conf import settings
from django.core.mail import send_mail
from django.template import Engine, Context
from django.utils.log import AdminEmailHandler
from django.views.debug import ExceptionReporter

log_except = logging.getLogger("except")

default_filter_str = ["'", '"', "\n", "\n\r", "\r\n", ]


class DictTool(dict):
    """
    以类属性的方式访问Dict的元素

    example:
    >>> p = DictTool({"a":1, "b":1110, "ss":{"nn":1, "nns":00}})
    >>> p.ss.nn
    1

    """

    def __getattr__(self, key):
        value = self.get(key, None)
        if value is None:
            return value

        if isinstance(value, dict):
            return DictTool(value)
        else:
            return value


def var_log_uuid(
        _uuid: str = None,
        request=None,
):
    x_request_id = getattr(request, 'x_request_id', None) \
        if request is not None and hasattr(request, 'x_request_id') else None
    if not x_request_id:
        x_request_id = uuid.uuid4() if not _uuid else _uuid
    return {"log_trace_id": x_request_id}


def fmt_error(log, title: str, e: Exception, other='', request=None, tag=None, log_trace_dict: dict = {}):
    """
    提取 Log Error 错误栈

    :param log:                 log instance eg: log_validate = logging.getLogger("validate")
    :param title:               log 标题
    :param e:                   log 错误栈 Exception
    :param other:               log 辅助性描述
    :param request:             django request 辅助性描述
    :param tag:                 日志tag 辅助性描述
    :param log_trace_dict:      日志trace_id 辅助性跟踪日志
    :return:
    """

    if request is not None:
        error_uri_str = f"当前请求异常路径uri={request.build_absolute_uri()}"
        request_id_str = f"当前请求request_id={request.META.get('HTTP_X_REQUEST_ID', '')}"
    else:
        error_uri_str = ""
        request_id_str = ""

    if not log_trace_dict and request:
        log_trace_dict = var_log_uuid(request=request)
    log_trace_id = log_trace_dict.get("log_trace_id", "-")
    traceback_format = traceback.format_exc()
    log.error(
        {
            "msg": {
                "error_type": str(type(e)),
                "error_message": str(e),
                "other": other,
                "title": f"{getattr(settings, 'PROJECT_NAME', 'django')}-"
                         f"{getattr(settings, 'DOMAIN', 'undefined-your-site-domain')}",
                "error_uri": error_uri_str,
                "request_id": request_id_str,
                "traceback": traceback_format,
            },
            "tag": tag or ['异常日志', ],
            "log_trace_id": log_trace_dict,
        }
    )
    if settings.DEBUG:
        # print error traceback
        print("===================== START  {0},错误={1}, {2}  START =====================".format(title, e, other))
        traceback.print_exc()

    else:
        # new thread send email error log
        trace_id = request_id_str or log_trace_id
        thr = Thread(
            target=core_send_mail,
            args=(
                f"{title}{f'-trace_id={trace_id}'}",
                traceback.format_exc(),
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMINS[0][1]]
            )
        )
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
    log_except.info({"msg": f"core_send_mail subject={subject}, message={message}, from_email={from_email},"
                            f"recipient_list={recipient_list} 发送状态 {send_status}", "tag": ["异常日志"]})


DEBUG_ENGINE = Engine(
    debug=True,
    libraries={"i18n": "django.templatetags.i18n"},
)


class FmtExceptionReporter(ExceptionReporter):
    def __int__(self, request, exc_type, exc_value, tb, is_email=False):
        super().__int__(request, exc_type, exc_value, tb, is_email=is_email)

    def get_traceback_data(self, **kwargs):
        ctx = super().get_traceback_data()
        return {**ctx, **kwargs}

    def get_traceback_html(self, **kwargs):
        """Return HTML version of debug 500 HTTP error page."""
        with self.html_template_path.open(encoding="utf-8") as fh:
            t = DEBUG_ENGINE.from_string(fh.read())
        c = Context(self.get_traceback_data(**kwargs), use_l10n=False)
        return t.render(c)


class FmtEmailHandler(AdminEmailHandler):
    """An exception log handler that emails log entries to site admins.

    If the request is passed as the first argument to the log record,
    request data will be provided in the email report.
    """

    def __init__(
            self,
            include_html=False,
            email_backend=None,
            reporter_class=None,
            **kwargs

    ):
        super().__init__(
            include_html=include_html,
            email_backend=email_backend,
            reporter_class=reporter_class
        )
        self.include_html = include_html
        self.email_backend = email_backend
        self.reporter_class = FmtExceptionReporter
        self.kwargs = copy(kwargs)

    def emit(self, record):
        try:
            request = record.request
            subject = "%s (%s IP): %s" % (
                record.levelname,
                (
                    "internal"
                    if request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS
                    else "EXTERNAL"
                ),
                record.getMessage(),
            )
        except Exception:
            subject = "%s: %s" % (record.levelname, record.getMessage())
            request = None
        subject = self.format_subject(subject)

        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = self.reporter_class(request, is_email=True, *exc_info)
        message = "%s\n\n%s" % (
            self.format(no_exc_record),
            reporter.get_traceback_text(),
        )
        html_message = reporter.get_traceback_html() if self.include_html else None
        self.send_mail(subject, message, fail_silently=True, html_message=html_message)

    # def send_mail(self, subject, message, *args, **kwargs):
    #     mail.mail_admins(
    #         subject, message, *args, connection=self.connection(), **kwargs
    #     )

    def format_subject(self, subject):
        """
        Escape CR and LF characters.
        """
        return subject.replace("\n", "\\n").replace("\r", "\\r")

# json log
* source code `vendor.logger_helper.json_formatter_log.VerboseJSONFormatter`
```text
class VerboseJSONFormatter(JSONFormatter):
    """JSON log formatter with built-in log record attributes such as log level.

    Usage example::

        import logging

        import json_log_formatter

        json_handler = logging.FileHandler(filename='/var/log/my-log.json')
        json_handler.setFormatter(json_log_formatter.VerboseJSONFormatter())

        logger = logging.getLogger('my_verbose_json')
        logger.addHandler(json_handler)

        logger.error('An error has occured')

    The log file will contain the following log record (inline)::

        {
            "filename": "tests.py",
            "funcName": "test_file_name_is_testspy",
            "levelname": "ERROR",
            "lineno": 276,
            "module": "tests",
            "name": "my_verbose_json",
            "pathname": "/Users/bob/json-log-formatter/tests.py",
            "process": 3081,
            "processName": "MainProcess",
            "stack_info": null,
            "thread": 4664270272,
            "threadName": "MainThread",
            "message": "An error has occured",
            "time": "2021-07-04T21:05:42.767726"
        }

    Read more about the built-in log record attributes
    https://docs.python.org/3/library/logging.html#logrecord-attributes.

    """

    def json_record(self, message, extra, record):
        extra['asctime'] = extra.get("asctime", f"{datetime.now()}")
        extra['levelname'] = record.levelname
        extra['module'] = record.module
        extra['filename'] = record.filename
        extra['funcName'] = record.funcName
        extra['lineno'] = record.lineno
        extra['pathname'] = record.pathname
        extra['name'] = f"{record.name}:{record.module}:{record.funcName}:{record.lineno}"
        extra['process'] = record.process
        extra['processName'] = record.processName
        extra['stack_info'] = getattr(record, 'stack_info', None)
        extra['exc_info'] = self.formatException(record.exc_info) if hasattr(record, 'exc_info') else None
        extra['thread'] = record.thread
        extra['threadName'] = record.threadName
        extra['message'] = message
        return extra
```
* cat error.log
```text
{
  "time": "2023-04-07 16:40:14.056162",
  "levelname": "ERROR",
  "module": "fmt_log_exception",
  "filename": "fmt_log_exception.py",
  "funcName": "fmt_error",
  "lineno": 55,
  "pathname": "F:\\GitSpace\\MedChat\\apps\\Utils\\fmt_log_exception.py",
  "name": "keyVault:fmt_log_exception:fmt_error:55",
  "process": 13132,
  "processName": "MainProcess",
  "stack_info": null,
  "exc_info": "",
  "thread": 13112,
  "threadName": "c6574d89-5ebd-4bba-bae3-cf072ba917f8",
  "message": ""
}
{
  "time": "2023-04-07 16:41:14.574936",
  "levelname": "ERROR",
  "module": "fmt_log_exception",
  "filename": "fmt_log_exception.py",
  "funcName": "fmt_error",
  "lineno": 55,
  "pathname": "F:\\GitSpace\\MedChat\\apps\\Utils\\fmt_log_exception.py",
  "name": "keyVault:fmt_log_exception:fmt_error:55",
  "process": 21668,
  "processName": "MainProcess",
  "stack_info": null,
  "exc_info": "",
  "thread": 12824,
  "threadName": "995c482e-12b1-47d4-9a2f-dd07369b656f",
  "message": ""
}
```

* settings config
```python
from vendor.logger_helper.json_formatter_log import VerboseJSONFormatter

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(threadName)s [%(name)s:%(module)s.%(funcName)s:%(lineno)d] '
                      '[%(levelname)s] - %(message)s',

        },
        "json": {
            '()': VerboseJSONFormatter,
        }
    },
    'handlers': {
        'user_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './user_log.log',
            'maxBytes': 1024 * 1024 * 5 * 100,
            'backupCount': 5,
            'formatter': 'json',  # json 日志格式
        },
    },
    
    'loggers': {
        'user_log': {
            'handlers': ['user_log', ],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}


# usage:
import logging
log_default = logging.getLogger("user_log")

log_default.error(
    {}, # message 日志内容
    extra={}, # 扩展字段信息
    exc_info=True, # 是否输出 exc_info 信息
    stack_info=True# 是否输出 stack_info 信息
)

```

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: backends.py

@author: 'ovan'

@mtime: '2024/8/19'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from celery.exceptions import TaskRevokedError, TimeoutError
from django.conf import settings

from vendor.health_check.backends import BaseHealthCheckBackend
from vendor.health_check.exceptions import ServiceReturnedUnexpectedResult, ServiceUnavailable

from .tasks import add
from .util import timeout_control


@timeout_control(seconds=1)
def celery_work_status(queue_timeout: int, queue: str, result_timeout: int) -> bool:
    result = add.apply_async(
        args=[4, 4], expires=queue_timeout, queue=queue
    )
    result.get(timeout=result_timeout)
    return result.result != 8


class CeleryHealthCheck(BaseHealthCheckBackend):
    queue = getattr(settings, "HEALTHCHECK_CELERY_QUEUE", "celery")

    def check_status(self):
        timeout = getattr(settings, "HEALTHCHECK_CELERY_TIMEOUT", 1)
        result_timeout = getattr(settings, "HEALTHCHECK_CELERY_RESULT_TIMEOUT", timeout)
        queue_timeout = getattr(settings, "HEALTHCHECK_CELERY_QUEUE_TIMEOUT", timeout)
        try:
            if not celery_work_status(
                    queue_timeout=queue_timeout,
                    queue=self.queue,
                    result_timeout=result_timeout
            ):
                self.add_error(
                    ServiceReturnedUnexpectedResult("Celery returned wrong result")
                )
        except IOError as e:
            self.add_error(ServiceUnavailable("IOError"), e)
        except NotImplementedError as e:
            self.add_error(
                ServiceUnavailable(
                    "NotImplementedError: Make sure CELERY_RESULT_BACKEND is set"
                ),
                e,
            )
        except TaskRevokedError as e:
            self.add_error(
                ServiceUnavailable(
                    "TaskRevokedError: The task was revoked, likely because it spent "
                    "too long in the queue"
                ),
                e,
            )
        except TimeoutError as e:
            self.add_error(
                ServiceUnavailable(
                    "TimeoutError: The task took too long to return a result"
                ),
                e,
            )
        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
        except ConnectionRefusedError as e:
            self.add_error(ServiceUnavailable("ConnectionRefusedError error"), e)

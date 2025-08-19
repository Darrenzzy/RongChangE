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
from django.db import DatabaseError, IntegrityError, OperationalError, ProgrammingError, DataError
from django.db import connections

from vendor.health_check.backends import BaseHealthCheckBackend
from vendor.health_check.exceptions import ServiceReturnedUnexpectedResult, ServiceUnavailable


class DatabaseBackend(BaseHealthCheckBackend):
    def check_status(self):

        try:
            connection = connections['default']
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        except OperationalError:
            raise ServiceReturnedUnexpectedResult("OperationalError")
        except IntegrityError:
            raise ServiceReturnedUnexpectedResult("Integrity Error")
        except ProgrammingError:
            raise ServiceReturnedUnexpectedResult("ProgrammingError")
        except DataError:
            raise ServiceReturnedUnexpectedResult("DataError")
        except DatabaseError:
            raise ServiceUnavailable("Database error")
        except Exception as e:
            raise ServiceReturnedUnexpectedResult(f"Unexpected error: {e}")

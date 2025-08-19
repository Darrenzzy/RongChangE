#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: china_time.py

@author: 'ovan'

@mtime: '2023/6/1'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import time
from datetime import datetime, timezone, timedelta


def get_china_now():
    """
    绝对的utc+8时间戳  0000000000.0
    :return:
    :rtype:
    """
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    obj = utc_now.astimezone(timezone(timedelta(hours=8)))
    obj = datetime(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second, obj.microsecond)
    return time.mktime(obj.timetuple())

# if __name__ == '__main__':
#     print(get_china_now())

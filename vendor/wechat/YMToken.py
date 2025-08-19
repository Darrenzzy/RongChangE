#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: YMToken.py

@author: 'Ovan'

@mtime: '2018/8/13'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""

import datetime
import hashlib

from vendor.wechat import DEFAULT_SALT_STR


class PullToken(object):
    """
    获取 token 悦米接口必备
    wx : 微信公众号 代码
    """

    def __init__(self, wx):
        self.wx = wx

    def getYMtoken(self):
        today = datetime.datetime.now().strftime("%Y%m%d%H")
        salt = DEFAULT_SALT_STR
        str_arr = "".join(sorted([self.wx, salt, today]))
        str_arr = hashlib.sha1(str_arr.encode('utf-8')).hexdigest()
        return str_arr.lower()


if __name__ == '__main__':
    token = PullToken('bolelife').getYMtoken()
    # 2e997ef093826da4f4155d6529edd645163e1fe3
    print('token :', token)

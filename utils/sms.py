#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: SmsSend.py

@author: 'Ovan'

@mtime: '2018/9/6'

@desc:


    `````````````````````````````````


---------------------------------------------------
"""

from random import choice, randint
from django.conf import settings
from django.core.cache import cache
import json
import logging
import requests

logger = logging.getLogger('user_log')


class SMS(object):
    """
    短信 发送 业务
    """
    SUCCESS_CODE = '0'

    @classmethod
    def send(cls, phone: str):
        code = ''.join([str(randint(0, 9)) for _ in range(6)])
        notify = f"【{settings.SMS_SIGNATURE}】感谢注册免e学苑，您的验证码为{code} (有效期为10分钟），请勿泄露给他人，如非本人操作，请忽略此信息。"

        params = {
            "account": settings.SMS_ACCOUNT,
            'password': settings.SMS_PASSWORD,
            "phone": phone,
            "msg": notify
        }
        try:
            response = requests.post(settings.SMS_SINGLE_SEND_URL, json=params)
        except Exception:
            return False
        result = response.json()
        logger.info(f'发送短信 TO: {phone} , CODE: {code}, params={params}。 响应数据: {result} .')

        is_success = result['code'] == cls.SUCCESS_CODE
        if is_success:
            cache.set(f'sms:code:{phone}:latestCode', code, settings.SMS_VALID_SECONDS)
            cache.set(f'sms:code:{phone}:latestSend', 1, settings.SMS_SEND_INTERVAL)
        return is_success


class ServerDomainSendSms(object):
    """
    根据域名动态 匹配 发送短信
    """

    def __init__(self):
        self.single_send_url = settings.SMS_SINGLE_SEND_URL

    def send_sms(self, signature, account, password, code, mobile):
        parmas = {
            "account": account,
            'password': password,
            "phone": mobile,
            "msg": f"【免e学苑】感谢注册免e学苑，您的验证码为{code} (有效期为10分钟），请勿泄露给他人，如非本人操作，请忽略此信息。"
        }

        response = requests.post(self.single_send_url, json=parmas)
        re_dict = json.loads(response.text)
        logger.info(
            '公司 %s 发送短信 TO: %s CODE: %s, parmas=%s。 响应数据: %s .' % (signature, mobile, code, parmas, re_dict)
        )
        return re_dict


def redis_sms_max_count_day(account: str, top: int = 10):
    """
    当日发送量最大计数上限
        如：短信验证码 24小时内限制 10 条
    :param account: 账号
    :param top:     账号最大次数上限
    :return:        bool
    """

    count = cache.get(f"sms:count:{account}")
    return int(count) >= top if count else False


def redis_sms_ttl(account):
    """
    验证码发送频率
    :param account:
    :return:
    """

    return cache.ttl("sms:%s" % account)


def redis_sms_get(account: str):
    """
    查询验证码
    :param account:
    :return:
    """

    return cache.get(f"sms:{account}")


def redis_sms_write(account: str, sms_code: str):
    """
    发送成功后，记录
    :param account:
    :param sms_code:
    :return:
    """

    send_key = f"sms:{account}"
    cache.set(send_key, sms_code, timeout=600)

    lock_ley = f"sms:count:{account}"
    cache.incr(lock_ley) if cache.has_key(lock_ley) else cache.set(lock_ley, 1, timeout=60 * 60 * 24)

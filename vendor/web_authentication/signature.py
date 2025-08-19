#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: param_dict_sign.py

@author: Ovan

@mtime: 2022/5/5 16:05

@Software  : PyCharm

@desc:


    `````````````````````````````````

---------------------------------------------------
"""
import hashlib
import logging
import random
import string
import time
import typing
from collections import OrderedDict

from vendor.web_authentication.china_time import get_china_now


# use loguru file log
# logger_plus.add(
#     './logs/z_{time}.log',
#     level='DEBUG',
#     format='{time:YYYY-MM-DD :mm:ss} - {level} - {file} - {line} - {message}',
#     rotation="10 MB"
# )


class SignatureHelper(object):
    """
    Signature Helper
    """

    def __init__(
            self,
            logger: logging.Logger,
            key_name: str = "x-appid",

    ):
        """key_name: 控制 签名参数名称 可用于 服务端接口交互，前端交互
            如: x-appid、openid、clientID 等

        :param str key_name:          自定义控制当前键名 x-appid, 自定义修改调整，亦可以通过 update_key_name 来调整
        :param logging.Logger logger: 自定义logger，若未指定将采用默认指定的 loguru ，请执行命令： pip install loguru

        """
        self.key_name = key_name
        self.logger = logger

    def update_key_name(self, key_name: str):
        """更新调整 key name

        :param str key_name:

        :returns:

        """
        self.key_name = key_name

    @staticmethod
    def create_sign(params: typing.Dict[str, str], filter_null: bool = False) -> str:
        """
        生成签名参数字符串
            - 并按照参数名ASCII字典序排序
            - filter_null 过滤掉字段为空时 不加入排序

        :param typing.Dict[str, str] params:    需参数名 ASCII 字典序排序 的 map
        :param bool filter_null:                是否需要过滤字段值为空的不计入签名计算

        :returns:   根据params得到排序后的签名字符串
        :rtype:     str

        """

        order_params = OrderedDict()
        for key in sorted(params.keys()):
            if filter_null:
                if params[key]:
                    order_params.update({key: params[key]})
            else:
                order_params.update({key: params[key]})

        # params_str = "&".join(["{}={}".format(quote(key), quote(str(vl))) for key, vl in order_params.items()])
        params_str = "&".join([f"{key}={vl}" for key, vl in order_params.items()])
        return params_str

    def get_temp_signature(
            self,
            appid: str,
            app_secret: str,
            # x_protection_uuid: str,
            client_version: str,
            client_source: str,
            api_version: str,
            extra_map: typing.Dict = {},
            timestamp: str = None,
            nonce_str: str = None,
    ) -> typing.Dict[str, str]:
        """生成 测试用的 数字签名

        :param str appid:                   签名用户信息主体字段键名，由 self.key_name 控制
        :param str app_secret:              签名参与计算的 密钥，不会参与网络请求明文传输
        # :param str x_protection_uuid:     签名参与计算的 用户标识
        :param str client_version:          签名参与计算的 客户端版本，如 安卓版本、浏览器版本号 ...
        :param str client_source:           签名参与计算的 客户端来源，如 安卓、苹果、xxx浏览器 ...
        :param str api_version:             签名参与计算的 服务端api版本号，如 V1、V2 ...
        :param Dict timestamp:              参签名参与计算的 时间戳
        :param Dict nonce_str:              参签名参与计算的 随机字符串
        :param Dict extra_map:              参与计算签名的扩展字段，可以动态添加其余字段参数 ...
        :returns:   构建组合后的含参与 signature 计算的所有参数map
        :rtype:     typing.Dict[str, str]

        """

        nonce = nonce_str if nonce_str else "".join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

        _params = {
            self.key_name: appid,
            'x-timestamp': timestamp if timestamp else f"{int(time.time() * 1000)}",
            'x-noncestr': nonce,
            # 'x-protection-uuid': x_protection_uuid,
            "x-client-version": client_version,
            "x-client-source": client_source,
            "x-api-version": api_version,
            **extra_map
        }
        _sign = self.create_sign(_params)
        print(f"_sign={_sign}")

        x_signature = hashlib.sha256(f"{_sign}&key={app_secret}".encode('utf-8')).hexdigest().lower()

        _params['x-signature'] = x_signature
        print(f"_params={_params}")
        return _params

    def validate_params(
            self, appid: str,
            app_secret: str,
            nonce: str,
            timestamp: int,
            signature: str,
            # x_protection_uuid: str,
            client_version: str,
            client_source: str,
            api_version: str,
            threshold: typing.Union[None, int] = 1 * 60 * 1000,
            extra_map: typing.Dict = {},
    ) -> bool:
        """校验参数签名

        :param str appid:                   签名用户信息主体字段键名，由 self.key_name 控制
        :param str app_secret:              签名参与计算的 密钥，不会参与网络请求明文传输
        :param str nonce:                   签名参与计算的 随机字符串
        :param int timestamp:               签名参与计算的 13位时间戳 精确到ms
        :param str signature:               sign签名数据值，由其他签名参数计算生成
        # :param str x_protection_uuid:     签名参与计算的 用户标识
        :param str client_version:          签名参与计算的 客户端版本，如 安卓版本、浏览器版本号 ...
        :param str client_source:           签名参与计算的 客户端来源，如 安卓、苹果、xxx浏览器 ...
        :param str api_version:             签名参与计算的 服务端api版本号，如 V1、V2 ...
        :param int threshold:               解析计算入参 时间戳 timestamp 的 有效阈值，默认1分钟的有效期时延，即 请求后该签名在三分钟内才有效
        :param Dict extra_map:              参与计算签名的扩展字段，可以动态添加其余字段参数 ...

        :returns:   是否通过签名校验
        :retype:    bool

        """

        # 1. build params
        _params = {
            self.key_name: appid,
            'x-timestamp': f"{timestamp}",
            'x-noncestr': nonce,
            "x-client-version": client_version,
            "x-client-source": client_source,
            "x-api-version": api_version,
            **extra_map
        }

        if threshold is not None:
            current_ts = int(get_china_now() * 1000)
            sub_timestamp = (current_ts + threshold) - timestamp
            val_timestamp_result = 0 <= sub_timestamp

            msg = f"signature timestamp validate params={_params},current_ts={current_ts},timestamp={timestamp}, " \
                  f"threshold={threshold}, result={val_timestamp_result}, sub_timestamp={sub_timestamp};"
            self.logger.info({"msg": msg, "tag": ["Api签名"]})

            if not val_timestamp_result:
                return False

        # 2. create sign
        _sign = self.create_sign(_params)

        # 3. create signature
        _signature = hashlib.sha256(f"{_sign}&key={app_secret}".encode('utf-8')).hexdigest().lower()
        _params['x-signature'] = _signature

        b = (_signature == signature)

        msg = f"signature validate result={b}. _params={_params}. your signature={signature}."
        self.logger.info({"msg": msg, "tag": ["Api签名"]})

        return b

# default signature
# APISignature = SignatureHelper()

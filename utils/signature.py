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
from typing import Dict, Union
from collections import OrderedDict


LogLevel = int


class SignatureHelper(object):
    """
    Signature Helper
    """

    def __init__(self, key_name: str = "x-appid", logger: Union[logging.Logger, None] = None):
        """key_name: 控制 签名参数名称 可用于 服务端接口交互，前端交互
            如: x-appid、openid、clientID 等

        :param str key_name:          自定义控制当前键名 x-appid, 自定义修改调整，亦可以通过 update_key_name 来调整
        :param logging.Logger logger: 自定义logger

        """
        self.key_name = key_name
        self._logger = logger

        self.logger("start SignatureHelper logging ...")
    
    def logger(self, msg: str, level: LogLevel=logging.INFO) -> None:
        if self._logger:
            self._logger.log(level, msg)

    def update_key_name(self, key_name: str):
        """更新调整 key name

        :param str key_name:

        :returns:

        """
        self.key_name = key_name

    @staticmethod
    def create_sign(params: Dict[str, str], filter_null: bool = False) -> str:
        """
        生成签名参数字符串
            - 并按照参数名ASCII字典序排序
            - filter_null 过滤掉字段为空时 不加入排序

        :param Dict[str, str] params:    需参数名 ASCII 字典序排序 的 map
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
            self, appid: str,
            app_secret: str,
            client_version: str,
            client_source: str,
            api_version: str
    ) -> Dict[str, str]:
        """生成 测试用的 数字签名

        :param str appid:           签名用户信息主体字段键名，由 self.key_name 控制
        :param str app_secret:      签名参与计算的 密钥，不会参与网络请求明文传输
        :param str client_version:  签名参与计算的 客户端版本，如 安卓版本、浏览器版本号 ...
        :param str client_source:   签名参与计算的 客户端来源，如 安卓、苹果、xxx浏览器 ...
        :param str api_version:     签名参与计算的 服务端api版本号，如 V1、V2 ...

        :returns:   构建组合后的含参与 signature 计算的所有参数map
        :rtype:     Dict[str, str]

        """

        nonce = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

        _params = {
            self.key_name: appid, 'x-timestamp': f"{int(time.time() * 1000)}", 'x-noncestr': nonce,
            "x-client-version": client_version, "x-client-source": client_source, "x-api-version": api_version,
        }
        _sign = self.create_sign(_params)

        x_signature = hashlib.md5(f"{_sign}&key={app_secret}".encode('utf-8')).hexdigest().lower()

        _params['x-signature'] = x_signature
        return _params

    def validate_params(
            self, appid: str,
            app_secret: str,
            nonce: str,
            timestamp: int,
            signature: str,
            client_version: str,
            client_source: str,
            api_version: str,
            threshold: int = 3 * 60 * 1000
    ) -> bool:
        """校验参数签名

        :param str appid:           签名用户信息主体字段键名，由 self.key_name 控制
        :param str app_secret:      签名参与计算的 密钥，不会参与网络请求明文传输
        :param str nonce:           签名参与计算的 随机字符串
        :param int timestamp:       签名参与计算的 13位时间戳 精确到ms
        :param str signature:       sign签名数据值，由其他签名参数计算生成
        :param str client_version:  签名参与计算的 客户端版本，如 安卓版本、浏览器版本号 ...
        :param str client_source:   签名参与计算的 客户端来源，如 安卓、苹果、xxx浏览器 ...
        :param str api_version:     签名参与计算的 服务端api版本号，如 V1、V2 ...
        :param int threshold:       解析计算入参 时间戳 timestamp 的 有效阈值，默认3分钟的有效期时延，即 请求后该签名在三分钟内才有效

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
        }

        sub_timestamp = int(time.time() * 1000) - timestamp
        val_timestamp_result = (0 <= sub_timestamp <= threshold)

        msg = f"signature validate params={_params}, result={val_timestamp_result}, sub_timestamp={sub_timestamp};"
        self.logger(msg)

        if not val_timestamp_result:
            return False

        # 2. create sign
        _sign = self.create_sign(_params)

        # 3. create signature
        _signature = hashlib.md5(f"{_sign}&key={app_secret}".encode('utf-8')).hexdigest().lower()
        _params['x-signature'] = _signature

        b = (_signature == signature)

        msg = f"signature validate result={b}. _params={_params}. your signature={signature}."
        self.logger(msg)

        return b


# default signature
APiSignature = SignatureHelper()

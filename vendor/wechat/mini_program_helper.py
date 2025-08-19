#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: mini_program_hepler.py

@author: 'ovan'

@mtime: '2023/5/5'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import json
import logging
from typing import Dict

import requests
from django.conf import settings
from django.core.cache import cache

from vendor.abnormal.fmt_log_exception import fmt_error

log_wechat = logging.getLogger("miniprogram")


class MINIProgram(object):
    def __init__(self):
        self.domain = "https://api.weixin.qq.com"

    def get_token(self, threshold: int = 0):
        """
        获取  api getAccessToken
        reference:
            - https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-access-token/getAccessToken.html
        """

        if threshold >= 3:
            # raise AssertionError("微信小程序getAccessToken异常")
            log_wechat.error({"msg": "微信小程序getAccessToken异常，阈值上限！", "tag": ["微信小程序"]})
            return ""

        cache_token_name = f"miniprogram:AccessToken:{settings.CHAT_APP_ID}"
        access_token = cache.get(cache_token_name)
        if access_token and threshold == 0:
            return access_token

        link = f"{self.domain}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": settings.CHAT_APP_ID,
            "secret": settings.CHAT_APPSECRECT
        }
        resp = requests.get(url=link, params=params)

        # 1. fail
        # 错误码	错误码取值	解决方案
        # -1	system error	系统繁忙，此时请开发者稍候再试
        # 40001	invalid credential  access_token isinvalid or not latest	获取 access_token 时 AppSecret 错误，
        #       或者 access_token 无效。请开发者认真比对 AppSecret 的正确性，或查看是否正在为恰当的公众号调用接口
        # 40013	invalid appid	不合法的 AppID ，请开发者检查 AppID 的正确性，避免异常字符，注意大小写
        # {
        #     "errcode": 40013,
        #     "errmsg": "invalid appid"
        # }
        #
        #
        # 2. success
        # {
        # "access_token":"ACCESS_TOKEN",
        # "expires_in":7200
        # }

        try:
            result = resp.json()
            log_wechat.info({"msg": f"微信小程序 getAccessToken link={link}, params={params}, result={result}",
                             "tag": ["微信小程序"]})
            if "errcode" in result and result.get("errcode") in [-1, 40001]:
                # retry
                threshold_ = threshold + 1
                log_wechat.info({"msg": f"微信小程序 getAccessToken 发生重试，threshold_={threshold_}, result={result}",
                                 "tag": ["微信小程序"]})
                return self.get_token(threshold=threshold_)

            if result.get("access_token") and result.get("expires_in"):
                cache.set(cache_token_name, result.get("access_token"), timeout=result.get("expires_in") - 50)

            return result.get("access_token", '')

        except Exception as e:
            fmt_error(
                log=log_wechat,
                title="微信小程序 getAccessToken 失败",
                e=e,
                other=f"link={link}, params={params}, result={resp.content.decode()}"
            )
            return ""

    def jscode2session(self, code: str, threshold: int = 0) -> Dict:
        """
        小程序登入
            - reference：
                https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html#%E8%B0%83%E7%94%A8%E7%A4%BA%E4%BE%8B

        :param code:
        :type code:
        :param threshold:
        :type threshold:
        :return:
        :rtype:
        """

        if threshold >= 3:
            log_wechat.error({"msg": "小程序登入 异常，阈值上限！", "tag": ["微信小程序"]})
            return {}

        link = f"{self.domain}/sns/jscode2session"
        params = {
            "grant_type": "authorization_code", "appid": settings.CHAT_APP_ID,
            "secret": settings.CHAT_APPSECRECT, "js_code": code
        }
        resp = requests.get(url=link, params=params)

        try:
            result = resp.json()
            log_wechat.info({"msg": f"小程序登入 link={link}, params={params}, result={result}", "tag": ["微信小程序"]})
            if result.get("errcode") in [-1, 40001]:
                # retry
                threshold_ = threshold + 1
                log_wechat.info(
                    {"msg": f"小程序登入 发生重试，threshold_={threshold_}, result={result}", "tag": ["微信小程序"]})
                return self.jscode2session(code=code, threshold=threshold_)

            # if result.get("errcode") == 0 and result.get("errmsg") == "ok":
            #     if "session_key" in result:
            #         result.pop("session_key")

            if "session_key" in result:
                result.pop("session_key")

            return result

        except Exception as e:
            fmt_error(
                log=log_wechat,
                title="小程序登入 失败",
                e=e,
                other={"link": link, "params": params, "result": resp.text}
            )
            return {}

    def get_user_phone(self, code: str, threshold: int = 0) -> Dict:
        """
        获取 小程序用户手机号
            - reference：
                https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-info/phone-number/getPhoneNumber.html#%E8%B0%83%E7%94%A8%E6%96%B9%E5%BC%8F

        :param code: code换取用户手机号。 说明，每个code只能使用一次，code的有效期为5min。前端触发提供
        :type code: str
        :param threshold:
        :type threshold:
        :return:
        :rtype:
        """

        if threshold >= 3:
            log_wechat.error({"msg": "微信小程序用户手机号 异常，阈值上限！", "tag": ["微信小程序"]})
            return {}

        link = f"{self.domain}/wxa/business/getuserphonenumber?access_token={self.get_token(threshold=threshold)}"
        params = json.dumps({"code": code})
        resp = requests.post(url=link, data=params, headers={"Content-Type": "application/raw"})

        try:
            result = resp.json()
            log_wechat.info(
                {"msg": f"微信小程序用户手机号 link={link}, params={params}, result={result}", "tag": ["微信小程序"]})
            if result.get("errcode") in [-1, 40001]:
                # retry
                threshold_ = threshold + 1
                log_wechat.info({"msg": f"微信小程序用户手机号 发生重试，threshold_={threshold_}, result={result}",
                                 "tag": ["微信小程序"]})
                return self.get_user_phone(code=code, threshold=threshold)

            # if result.get("errcode") == 0 and result.get("errmsg") == "ok":
            #     '''
            #     {
            #         "errcode":0,
            #         "errmsg":"ok",
            #         "phone_info": {
            #             "phoneNumber":"xxxxxx",
            #             "purePhoneNumber": "xxxxxx",
            #             "countryCode": 86,
            #             "watermark": {
            #                 "timestamp": 1637744274,
            #                 "appid": "xxxx"
            #             }
            #         }
            #     }
            #     '''
            #     # return result.get("phone_info", {})
            #     return result
            return result

            # return {}

        except Exception as e:
            fmt_error(
                log=log_wechat,
                title="微信小程序用户手机号 失败",
                e=e,
                other={"link": link, "params": params, "result": resp.text}
            )
            return {}

    def query_scheme(
            self,
            scheme: str,
            threshold: int = 0
    ):
        """
        查询scheme码
        reference:
            - https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/url-scheme/queryScheme.html
        """
        if threshold >= 3:
            log_wechat.error({"msg": "微信小程序 query_scheme 异常，阈值上限！", "tag": ["微信小程序"]})
            return {}

        link = f"{self.domain}/wxa/queryscheme?access_token={self.get_token(threshold=threshold)}"
        params = {"scheme": scheme}

        resp = requests.post(url=link, json=params)

        try:
            result = resp.json()
            log_wechat.info({"msg": f"微信小程序 query_scheme link={link}, params={params}, result={result}",
                             "tag": ["微信小程序"]})
            if result.get("errcode") in [-1, 40001]:
                # retry
                threshold_ = threshold + 1
                log_wechat.info({"msg": f"微信小程序 query_scheme 发生重试，threshold_={threshold_}, result={result}",
                                 "tag": ["微信小程序"]})
                return self.query_scheme(scheme=scheme, threshold=threshold_)

            # if result.get("errcode") == 0 and result.get("errmsg") == "ok":
            #     return result
            return result

            # return {}

        except Exception as e:
            fmt_error(
                log=log_wechat,
                title="微信小程序 query_scheme 失败",
                e=e,
                other=f"link={link}, params={params}, result={resp.content.decode()}"
            )
            return {}

    def generate_scheme(
            self,
            path: str,
            query: str,
            env_version: str,
            threshold: int = 0
    ):
        """
        获取scheme码
        reference:
            - https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/url-scheme/generateScheme.html
        """
        if threshold >= 3:
            log_wechat.error({"msg": "微信小程序 generate_scheme 异常，阈值上限！", "tag": ["微信小程序"]})
            return ''

        link = f"{self.domain}/wxa/generatescheme?access_token={self.get_token(threshold=threshold)}"
        params = {
            "jump_wxa": {
                "path": path,
                "query": query,
                "env_version": env_version
            }
        }

        resp = requests.post(url=link, json=params)

        try:
            result = resp.json()
            log_wechat.info({"msg": f"微信小程序 generate_scheme link={link}, params={params}, result={result}",
                             "tag": ["微信小程序"]})

            if result.get("errcode") in [-1, 40001]:
                # retry
                threshold_ = threshold + 1
                log_wechat.info(
                    {"msg": f"微信小程序 generate_scheme 发生重试，threshold_={threshold_}, result={result}",
                     "tag": ["微信小程序"]}
                )
                return self.generate_scheme(path=path, query=query, env_version=env_version, threshold=threshold_)

            if result.get("errcode") == 0 and result.get("errmsg") == "ok":
                return result.get("openlink", '')

            return ''

        except Exception as e:
            fmt_error(
                log=log_wechat,
                title="微信小程序 generate_scheme 失败",
                e=e,
                other=f"link={link}, params={params}, result={resp.content.decode()}"
            )
            return ''


default_mini_program_client = MINIProgram()

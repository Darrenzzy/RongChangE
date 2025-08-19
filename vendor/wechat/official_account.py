#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: userinfo.py

@author: 'ovan'

@mtime: '2019/4/17'

@desc:


    `````````````````````````````````


---------------------------------------------------
"""

import json
import logging
import datetime
import requests
from django.conf import settings
from vendor.wechat.YMToken import PullToken


logger = logging.getLogger("wechat")


class WeChatUserInfo(object):
    
    PAID_MSG = '平台已支付'
    AUDITED_MSG = '请分享作品给用户审核并确认'

    @classmethod
    @property
    def token(cls):
        """
        获取 YM api token
        """

        return PullToken(wx=settings.WX_CODE).getYMtoken()
    
    @classmethod
    @property
    def current_time(cls):
        return datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')

    @classmethod
    def get_user_subscribe_status(cls, openid):
        """
        获取openid的关注状态
        """

        status, rsp = cls.get_user(openid)
        if not status:
            return False
        return bool(rsp.get("subscribe", 0))

    @classmethod
    def get_user(cls, openid: str):
        """
        获取openid用户信息

        {
            "subscribe":1,
            "openid":"o3Jny6JBgyt_05EX8BwyVouZge0Q",
            "nickname":"右耳",
            "sex":1,
            "language":"zh_CN",
            "city":"连云港",
            "province":"江苏",
            "country":"中国",
            "headimgurl":"http://thirdwx.qlogo.cn/mmopen/ajNVdqHZLLBORibbgdBicrj4rwbLOmLSCibEdV9PoIq3iaPXFqKcX67O6snsvNdhrohXPxOwp9P4o1bB52UmSVRq9w/132",
            "subscribe_time":1622525940,
            "remark":"",
            "groupid":102,
            "tagid_list":[ 102, 105 ],
            "subscribe_scene":"ADD_SCENE_PROFILE_CARD",
            "qr_scene":0,
            "qr_scene_str":"",
            "headimg":"http://thirdwx.qlogo.cn/mmopen/ajNVdqHZLLBORibbgdBicrj4rwbLOmLSCibEdV9PoIq3iaPXFqKcX67O6snsvNdhrohXPxOwp9P4o1bB52UmSVRq9w/132"
        }

        :return:
        """

        url = f"{settings.WECHAT_DOMAIN}/api/getuserdetail"

        send_data = {"wx": settings.WX_CODE, "openid": openid, "token": cls.token}
        rt = requests.post(url, data=send_data)
        try:
            content = rt.json()
            logger.info(f"获取openid用户信息 => url={url}, send_data={send_data}, res_data={content}")
            return len(content.get("openid", "")) > 0, content

        except Exception as e:
            content = rt.text
            logger.error(f'获取openid用户信息异常 => openid={openid}, send_data={send_data}, res_data={content}, error={e}')
            return False, content

    @classmethod
    def send_template_msg(
        cls, 
        *, 
        tempid: str, 
        openids: list[str], 
        username: str,
        time: str,
        state: str, 
        url: str = ''
    ):
        """
        发送模板消息
        :param tempid: 模板ID
        :param openids: 发送对象openid
        :param username: 项目名称（作品标题）
        :param time: 时间
        :param state: 状态【认证通过、认证不通过】
        :param url: 跳转URL
        """

        template_data = {
            'openids': openids,
            'data': {
                'items': [
                    {'key': 'thing1', 'value': username},
                    {'key': 'const6', 'value': state},
                    {'key': 'time7', 'value': time},
                    {'key': 'first', 'value': ''},
                    {'key': 'remark', 'value': ''}
                ],
                'tempid': tempid,
                'url': url
            }
        }

        url = f'{settings.WECHAT_DOMAIN}/api/sendtempmsg?wx={settings.WX_CODE}&token={cls.token}'
        r = requests.post(url, json.dumps(template_data))
        logger.info(f"准备模板消息阶段 => data={template_data}")        

        try:
            rts = r.json()
            send_result = (rts['r'] == 0)
            logger.info(f"模板消息发送状态 => {send_result}, openid={openids}, send_data={template_data}, res_data={rts}")
        except Exception as e:
            logger.error(f"模板消息发送失败 => openids={openids}, send_data={template_data}, res_data={r.text}, error={e}")
            send_result = False
        return send_result

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: api.py

@author: 'ovan'

@mtime: '2024/5/11'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from typing import Optional

import requests


class FwAPI(object):
    """docs for Api:
        - https://apifox.com/apidoc/shared-23c8e217-fcd9-4b75-b983-039d787478d4
    """

    def __init__(self, app_id, app_secret, service_id):
        self.app_id = app_id
        self.app_secret = app_secret
        self.service_id = service_id
        self.host = 'https://fwapi.xiegangsh.com'

    def get_token(self):
        """
        获取token
        :return:
        """
        url = '/v1/auth/tokens'
        params = {
            "grant_type": "client_credentials",
            "client_id": self.app_id,
            "client_secret": self.app_secret
        }

        resp = requests.post(f"{self.host}{url}", json=params)
        print(f"get_token -> resp.status_code={resp.status_code}")
        print(f"get_token -> resp.headers={resp.headers}")
        if resp.status_code == 200 and resp.headers.get('Content-Type').lower().startswith('application/json'):
            resp_json = resp.json()
            print(f"resp_json={resp_json}")
            return resp_json.get("data", {}).get("access_token", '')
        else:
            raise Exception(f"获取token失败，{resp.text}")

    def get_sign_url(
            self,
            name: str,
            id_card_no: str,
            id_card_type: str,
            mobile: str,
            bank_card_no: str,
            servicer_id: Optional[int] = None,
            identity_front_url: Optional[str] = None,
            identity_back_url: Optional[str] = None,
    ):
        """获取签约地址
            - https://apifox.com/apidoc/shared-23c8e217-fcd9-4b75-b983-039d787478d4/api-171721602

        :param name:            姓名
        :param id_card_no:      证件号码
        :param id_card_type:    证件类型
        :param mobile:          手机号
        :param bank_card_no:    银行卡号
        :param servicer_id:     服务商id
        :param identity_front_url:     服务商id
        :param identity_back_url:     服务商id
        """

        url = '/v1/freelancers/add_and_sign_link'
        params = {
            "name": name,
            "id_card_no": id_card_no,
            "id_card_type": id_card_type,
            "mobile": mobile,
            "bank_card_no": bank_card_no,
            "servicer_id": servicer_id or self.service_id,
            "nation": None,
            "gender": None,
            "address": None,
            "identity_front_url": identity_front_url,
            "identity_back_url": identity_back_url,
        }
        headers = {
            'Authorization': self.get_token(),
        }
        print(f"params={params}")

        resp = requests.post(f"{self.host}{url}", json=params, headers=headers)
        print(f"get_sign_url -> resp.status_code={resp.status_code}")
        print(f"get_sign_url -> resp.headers={resp.headers}")

        if resp.status_code == 200 and resp.headers.get('Content-Type').lower().startswith('application/json'):
            resp_json = resp.json()
            print(f"resp_json={resp_json}")
            return resp_json.get("data", {}).get("sign_link", '')
        else:
            raise Exception(f"获取token失败，{resp.text}")

    def get_sign_status(self, id_card_no: str, servicer_id: Optional[int] = None):
        """查询签约状态
            - https://apifox.com/apidoc/shared-23c8e217-fcd9-4b75-b983-039d787478d4/api-171791392

        :param id_card_no:      证件号码
        :param servicer_id:     服务商id
        """
        url = '/v1/query-esign'
        params = {
            "idCardNo": id_card_no,
            "servicerId": servicer_id or self.service_id,
        }
        headers = {
            'Authorization': self.get_token(),
        }

        resp = requests.get(f"{self.host}{url}", params=params, headers=headers)
        print(f"get_sign_status -> resp.status_code={resp.status_code}")
        print(f"get_sign_status -> resp.headers={resp.headers}")

        if resp.status_code == 200 and resp.headers.get('Content-Type').lower().startswith('application/json'):
            resp_json = resp.json()
            print(f"resp_json={resp_json}")
            # n: 否 y:是
            return resp_json.get("data", {}).get("is_sign", False)
        else:
            raise Exception(f"获取token失败，{resp.text}")


if __name__ == '__main__':
    api = FwAPI(
        app_id='017ee35f-b28f-4550-8cf2-baf5167a38cd',
        app_secret='fb4f07c7-8911-407f-a4e6-c13a4778d475',
        service_id=1655511469409701888
    )

    # id_number = '411481198812025451'
    # phone_number = '17601301597'
    # name = '豆帅帅'
    # bank_card_number = '4188356781998190'
    id_number = '210623198906067029'
    phone_number = '15142449987'
    name = '于夕情'
    bank_card_number = '4188356781998191'

    sign_link = api.get_sign_url(
        name=name,
        id_card_no=id_number,
        id_card_type="0",
        mobile=phone_number,
        bank_card_no=bank_card_number,
        # servicer_id='',
        identity_front_url='https://zgwy-qn.yuemia.com/vendor/server/ocr/pdf2pdf/extract/table/page_6.png',
        identity_back_url='https://zgwy-qn.yuemia.com/vendor/server/ocr/pdf2pdf/extract/table/page_8.png',
    )
    print(f"sign_link={sign_link}")

    is_sign = api.get_sign_status(id_card_no=id_number)
    print(f"is_sign={is_sign}")

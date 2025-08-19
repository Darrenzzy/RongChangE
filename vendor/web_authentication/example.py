#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: example.py

@author: 'ovan'

@mtime: '2023/5/8'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import logging

log = logging.getLogger(__name__)


def test_signature():
    from vendor.web_authentication.signature import SignatureHelper
    signature = SignatureHelper(log)

    # x_protection_uuid="123",
    # x-api-version: V1
    # x-appid: mp_beckman
    # x-client-source: iPhone X
    # x-client-version: iOS 10.0.1-mp_8.0.5
    # x-noncestr: WBcQw0XgZXlA0DZ
    # x-signature: 5c0312f4e90bf023341d5e18269e0b2f
    # x-signature: ff1b2e94acf81c2fa7c3612e3ce6d0d3
    # x-timestamp: 1684310558655
    params = signature.get_temp_signature(
        appid="123",
        app_secret='123',
        client_version="client_version",
        client_source="client_source",
        api_version="api_version",
        extra_map={},
        timestamp='1684304010450',
        nonce_str='IIKlirAFh9ncsBx'
    )
    # {'x-appid': 'mp_beckman', 'x-timestamp': '1684308784331', 'x-noncestr': 'ye17QTMXlHpynjPTMhq5LokR1AiwsGwl',
    #  'x-client-version': 'iOS 10.0.1-mp_8.0.5', 'x-client-source': 'iPhone X', 'x-api-version': 'V1',
    #  'x-signature':
    #  'dd3ac2acc8c2ada4ec729fb12847c553'
    #   dd3ac2acc8c2ada4ec729fb12847c553
    #  }

    print(f"params={params}")


if __name__ == '__main__':
    test_signature()

    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: test.py

@author: 'ovan'

@mtime: '2024/4/3'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""


def abc():
    import requests

    # 请求的参数
    token_endpoint = 'https://login.microsoftonline.com/3ac94b33-9135-4821-9502-eafda6592a35'
    client_id = '99a4c52c-fc16-434c-9812-6af9516b827c'
    client_secret = "157a147a-86dc-439d-a32a-8d4b8e98f19a"
    scope = ["User.ReadBasic.All"]

    # 请求的数据
    data = {
        "grant_type": "code",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }

    # 发送 POST 请求获取访问令牌
    response = requests.post(token_endpoint, data=data)
    print(f"response: {response.text}")
    js = response.json()
    print(f"js={js}")


def mmm():
    import msal

    # 你的应用程序ID和重定向URI
    CLIENT_ID = '99a4c52c-fc16-434c-9812-6af9516b827c'
    REDIRECT_URI = 'http://localhost:8000/api/user/case/'
    AUTHORITY = 'https://login.microsoftonline.com/3ac94b33-9135-4821-9502-eafda6592a35'  # 或者你的Azure AD 租户ID

    # 创建msal客户端
    client = msal.PublicClientApplication(
        CLIENT_ID, authority=AUTHORITY
    )

    # 创建认证提示参数
    scopes = ["User.ReadBasic.All"]

    # 执行认证流程
    result = client.acquire_token_interactive(scopes)

    # 获取访问令牌
    access_token = result.get('access_token')

    # 使用访问令牌调用Microsoft Graph API获取用户信息
    # 这里只是一个示例，实际的API调用取决于你的需求
    import requests

    response = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': 'Bearer ' + access_token},
    )

    if response.status_code == 200:
        user_info = response.json()
        print(user_info)
    else:
        print(f'Error: {response.status_code}')


if __name__ == '__main__':
    mmm()

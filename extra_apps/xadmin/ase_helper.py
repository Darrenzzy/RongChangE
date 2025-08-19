#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: ace.py

@author: 'ovan'

@mtime: '2020/5/8'

@desc:


    `````````````````````````````````


---------------------------------------------------
"""
import base64
import hashlib
import typing

# from Crypto.Cipher import AES
# pip install pycryptodomex
from Cryptodome.Cipher import AES

_DEFAULT_AES_KEY = "QRfTkgVX2Xbvu1NwjxbifBbryU8mELrk"
_DEFAULT_AES_IV = 'rmuLiUlqROlezoAv'


class AESHelper(object):
    """
    信息加密 AES
    """

    def __init__(
            self, key: typing.Union[None, str, bytes] = None,
            iv: typing.Union[None, str, bytes] = None
    ):
        """

        :param key:     key
        :param iv:      iv lens must be 16

        """

        if (key is None and iv is None) or (isinstance(key, str) and isinstance(iv, str)):

            # 密钥  16 24 32
            key = key or _DEFAULT_AES_KEY

            # 向量  16
            iv = iv or _DEFAULT_AES_IV

            self.key_bytes = bytes(key, encoding='utf-8')
            self.iv = bytes(iv, encoding='utf-8')

        elif isinstance(key, bytes) and isinstance(iv, bytes):
            self.key_bytes, self.iv = key, iv

        else:
            raise ValueError("Key & IV must be bytes or str")

    def pkcs7padding(self, text: str) -> str:
        """
        明文使用PKCS7填充
        最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理

        :param str text: 待填充数据

        :return:        已完成填充的数据
        :rtype:         str

        """

        bs = AES.block_size  # 16
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        # tips：utf-8编码时，英文占1个byte，而中文占3个byte
        padding_size = length if (bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
        padding_text = chr(padding) * padding
        return text + padding_text

    def pkcs7unpadding(self, text: str) -> str:
        """处理使用PKCS7填充过的数据

        :param str text: 待解填充数据

        :return:    已解填充数据
        :rtype:     str

        """

        length = len(text)
        unpadding = ord(text[length - 1])
        return text[0:length - unpadding]

    def encrypt(self, content: str) -> str:
        """AES加密
                key,iv使用同一个
                模式cbc
                填充pkcs7

        :param str content: 待加密内容

        :return:    加密后的内容
        :rtype:     str

        """
        if not content:
            return ''

        # content = content.replace('$', '/').replace('!', '+')
        cipher = AES.new(self.key_bytes, AES.MODE_CBC, self.iv)
        # 处理明文
        content_padding = self.pkcs7padding(content)
        # 加密
        aes_encode_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        # 重新编码
        result = str(base64.b64encode(aes_encode_bytes), encoding='utf-8')
        # result = result.replace('/', '$').replace('+', '!')
        return result

    def decrypt(self, content: str) -> str:
        """AES 解密
                key,iv使用同一个
                模式cbc
                去填充pkcs7

        :param str content: 待解密内容

        :return:    解密后的内容
        :rtype:     str

        """
        if not content:
            return ''

        try:
            # 对方有个混淆
            # content = content.replace('$', '/').replace('!', '+')
            cipher = AES.new(self.key_bytes, AES.MODE_CBC, self.iv)
            # base64解码
            aes_encode_bytes = base64.b64decode(content)
            # 解密
            aes_decode_bytes = cipher.decrypt(aes_encode_bytes)
            # 重新编码
            result = str(aes_decode_bytes, encoding='utf-8')
            # 去除填充内容
            result = self.pkcs7unpadding(result)
        except Exception as e:
            return ""

        return "" if result is None else result


def utils_md5(keys_values: str) -> str:
    return hashlib.md5(keys_values.encode('utf-8')).hexdigest()


# Default aes client
AESClientDefault = AESHelper()

if __name__ == '__main__':
    # u = AESCRMUtils()
    # values = u.aes_encode("xxxxx")
    # print(f"encode = {values}")
    # print(f"decode = {u.aes_decode(values)}")
    # """
    # An1Cd5YzDnNX4Nh7wVOrAg==
    # IApnp!WBJ8fYmS8PUjdYiQ==
    # """

    pass

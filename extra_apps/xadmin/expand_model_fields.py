#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: fields.py

@author: 'ovan'

@mtime: '2020/6/1'

@desc:


    `````````````````````````````````


---------------------------------------------------
"""

from django.db import models

from xadmin.ase_helper import AESClientDefault


class EncryptedFieldException(Exception):
    pass


class EncryptedMixin(models.Field):
    internal_type = "CharField"
    prepared_max_length = None

    crypto = None

    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', self.prepared_max_length)
        if u"aes_client" in kwargs:
            # default aes client
            self.crypto = kwargs[u'aes_client']
            kwargs.pop(u"aes_client")

        else:
            self.crypto = AESClientDefault

        if self.crypto is None:
            raise EncryptedFieldException(
                "Field {} 必须参入加密方法实现类 crypto.".format(self.description)
            )
        if not hasattr(self.crypto, "encrypt") or not hasattr(self.crypto, "decrypt"):
            raise EncryptedFieldException(
                "Field {} 必须参入加密实现类 crypto 必须实现 decrypt/encrypt 方法.".format(self.description)
            )

        super(EncryptedMixin, self).__init__(**kwargs)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(EncryptedMixin, self).get_db_prep_value(value, connection, prepared)
        if value is not None:
            encrypted_text = self.crypto.encrypt(value)
            if self.max_length and len(encrypted_text) > self.max_length:
                raise EncryptedFieldException(
                    "Field {} max_length={} encrypted_len={}".format(self.name, self.max_length, len(encrypted_text))
                )
            return encrypted_text
        return None

    def from_db_value(self, value, expression, connection, *args):
        if value is not None:
            self_to_python = self.to_python(self.crypto.decrypt(value))
            return self_to_python
        return None

    def get_internal_type(self):
        return self.internal_type


class EncryptedCharField(EncryptedMixin, models.CharField):
    """
    加密 python解密回显，入库加密
        - 适用于 用户姓名加密
    """

    prepared_max_length = 600

    # def get_prep_lookup(self, lookup_type, value):
    #     """限制查询方式"""
    #     print(f"get_prep_lookup value={value}")
    #     return self.crypto.aes_encode(value)


class EncryptedEmailField(EncryptedMixin, models.EmailField):
    """
    加密 python解密回显，入库加密
        - 适用于 邮箱加密，邮箱入库后都是小写
    """

    prepared_max_length = 600

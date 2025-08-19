# -*- coding: utf-8 -*-


import base64
from pathlib import Path

# pip install pycryptodomex
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5 as PK_METHOD

from xadmin.cache import get_default_cache

local_cache = get_default_cache()

current_file_path = Path(__file__).resolve().parent
with open(f'{current_file_path / "private.pem"}', 'rb') as f:
    _PRI_KEY_ = f.read()
with open(f'{current_file_path / "public.pem"}', 'rb') as f:
    _PUB_KEY_ = f.read()


class RsaClient:
    """RSA 加密解密"""

    def __init__(self):
        """
        私钥生成：openssl genrsa -out private.pem 2048
        公钥生成：openssl rsa -in private.pem -pubout -out public.pem
        """
        try:
            self.pri_key_ = local_cache.get('rsa:login:pri_key')
            self.pub_key_ = local_cache.get('rsa:login:pub_key')
        except Exception as _:
            self.pri_key_ = _PRI_KEY_
            self.pub_key_ = _PUB_KEY_

    def generate_key(self):
        """生成密钥"""
        if not self.pri_key_:
            # 生成RSA密钥对
            key = RSA.generate(2048)
            self.pri_key_ = key.export_key()
            self.pub_key_ = key.publickey().export_key()
            # 过期时间为1周（60秒 * 60分钟 * 24小时 * 7天）
            local_cache.set('rsa:login:pri_key', self.pri_key_.decode(), 60 * 60 * 24 * 7)
            local_cache.set('rsa:login:pub_key', self.pub_key_.decode(), 60 * 60 * 24 * 7)

        return self.pri_key_, self.pub_key_

    def get_pub_key(self):
        """获取公钥"""
        self.generate_key()
        return RSA.import_key(self.pub_key_)

    def get_pri_key(self):
        """获取私钥"""
        self.generate_key()
        return RSA.import_key(self.pri_key_)

    @property
    def get_pub_cipher(self):
        """创建 公钥 密码器"""
        return PK_METHOD.new(self.get_pub_key())

    @property
    def get_pri_cipher(self):
        """创建 私钥 密码器"""
        return PK_METHOD.new(self.get_pri_key())

    def encrypt(self, param):
        """加密"""
        ciphertext = self.get_pub_cipher.encrypt(param.encode())
        return str(base64.b64encode(ciphertext), encoding='utf-8')

    def decrypt(self, bs64_ciphertext):
        """解密"""
        plaintext = self.get_pri_cipher.decrypt(base64.b64decode(bs64_ciphertext), sentinel=None)
        return plaintext.decode()


if __name__ == '__main__':
    # key = RSA.generate(2048)
    # pri_key_ = key.export_key()
    # pub_key_ = key.publickey().export_key()
    # with open('private.pem', 'wb') as f:
    #     f.write(pri_key_)
    #
    # with open('public.pem', 'wb') as f:
    #     f.write(pub_key_)

    # test = RsaClient()
    # print("*****************************")
    # us = test.encrypt("123")
    # print(f'u = {us}')
    # print(f'decrypt u = {test.decrypt(us)}')
    # ps = test.encrypt("xxx")
    # print(f'p = {ps}')
    # print(f'decrypt ps = {test.decrypt(ps)}')

    pass

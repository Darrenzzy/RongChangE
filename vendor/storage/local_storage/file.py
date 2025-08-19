#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: file.py

@author: 'ovan'

@mtime: '2023/5/24'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import pathlib

# from django.core.files import File
# from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings


def django_storage_save(location: pathlib.Path, name: str, file, max_length=None):
    """
    django local storage save file
    reference:
        - https://docs.djangoproject.com/en/4.2/topics/files/

    :param location:        存放文件的地址
    :type location:         文件绝对地址或者path
    :param name:            存储的文件名
    :type name:             str
    :param file:            文件对象
    :type file:
    :param max_length:      最大长度
    :type max_length:
    :return:                FileSystemStorage 文件对象, 存储的文件名称
    :rtype:
    """

    location = location or settings.BASE_DIR / "media/import/upload"
    if not location.exists():
        location.mkdir(parents=True)
    fs = FileSystemStorage(location=location)
    filename = fs.save(name, file, max_length)
    return fs, filename

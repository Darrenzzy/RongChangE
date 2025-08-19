#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: tools.py

@author: 'ovan'

@mtime: '2024/7/31'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import typing


def convert_array_to_dictionary(
        array: typing.List[typing.Dict],
        target_key_name: str = 'ymuser_id',
        drop_target_key=True,
) -> typing.Dict:
    """
    将数组对象转为dict
    >> [{'ymuser_id':1, 'other': 'xxx'}, {'ymuser_id':1, 'other': 'xxx2'}, {'ymuser_id':2, 'other': 'xxx'}, ]
    >> convert to dict: { 1:[{'other': 'xxx'}, {'other': 'xxx2'}], 2:[{'other': 'xxx'}]}

    :params drop_target_key: 返回字典内是否删除 target_key_name 避免数据重复
    """
    # 创建空字典
    dictionary = {}

    # 遍历数组对象
    for obj in array:
        ymuserId = obj.get(target_key_name)

        if drop_target_key:
            obj.pop(target_key_name)

        if ymuserId in dictionary:
            dictionary[ymuserId].append(obj)
        else:
            dictionary[ymuserId] = [obj]

    return dictionary

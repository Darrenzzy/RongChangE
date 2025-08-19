#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: recursive_tools.py

@author: 'ovan'

@mtime: '2020/9/11'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
import typing

"""
案例：
        [
            {
                "id": 2,
                "parent_id": 1.0,
                "title": "1.1级",
                "order": 2
            },
            {
                "id": 1,
                "parent_id": 0.0,
                "title": "一级",
                "order": 1
            },
            {
                "id": 4,
                "parent_id": 2.0,
                "title": "1.1.1",
                "order": 0
            },
            {
                "id": 5,
                "parent_id": 4.0,
                "title": "1.1..1.1",
                "order": 0
            }
        ]


转成父子嵌套结构的json

        [
            {
                "id": 1,
                "parent_id": 0.0,
                "title": "一级",
                "order": 1,
                "parents": [
                    {
                        "id": 2,
                        "parent_id": 1.0,
                        "title": "1.1级",
                        "order": 2,
                        "parents": [
                            {
                                "id": 4,
                                "parent_id": 2.0,
                                "title": "1.1.1",
                                "order": 0,
                                "parents": [
                                    {
                                        "id": 5,
                                        "parent_id": 4.0,
                                        "title": "1.1..1.1",
                                        "order": 0
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
"""


# data是某一級的數組
def get_children(data: typing.List, all_data: typing.List):
    """
    递归将 平面的数据结构第规程父子嵌套的json  案例见上方注释
    :param data:        在 all_data 中的某一层级[顶级]数据
    :param all_data:    所有数据
    :return:
    """

    for i in data:
        children = []
        for d in all_data:
            if d["parent_id"] == i["depart_id"]:
                children.append(d)

        if children:
            i["parents"] = get_children(children, all_data)

    return data

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: urls.py

@author: 'ovan'

@mtime: '2024/7/30'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from rest_framework.routers import SimpleRouter

from survey.views import DiseasesCategoryViewSet, QuestionBankViewSet, MyHistoryViewSet

router = SimpleRouter()

# 疾病分类
# list
router.register('category', DiseasesCategoryViewSet, basename='category')

# 随机组成题库
# list
# create
router.register('question', QuestionBankViewSet, basename='question')

# 我的调研问卷
# list
router.register('my-history', MyHistoryViewSet, basename='my-history')

urlpatterns = router.urls

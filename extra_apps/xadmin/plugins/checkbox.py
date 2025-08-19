#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: checkbox.py

@author: 'ovan'

@mtime: '2023/12/28'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from xadmin.sites import site
from xadmin.widgets import AdminCheckboxFormWidget
from xadmin.views import BaseAdminPlugin, ModelFormAdminView


class FormCheckboxPlugin(BaseAdminPlugin):

    def init_request(self, *args, **kwargs):
        return True

    def get_field_style(self, attrs, db_field, style, **kwargs):
        if style == 'form-checkbox':
            return {'widget': AdminCheckboxFormWidget}


site.register_plugin(FormCheckboxPlugin, ModelFormAdminView)

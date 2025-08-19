#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: w.py

@author: 'ovan'

@mtime: '2023/12/28'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""
from django import forms
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

from xadmin.util import vendor


class ImagePreviewWidget(AdminFileWidget):
    @staticmethod
    def widget_media():
        return forms.Media(
            css={
                'all': (
                    'path/to/css/file.css',
                )
            }
        )

    def render(self, name, value, attrs=None, renderer=None):
        output = []

        output.append('<style>')
        output.append('''
            .grid-4 img {
                width: 25%;
                height: 25%;
            }

            .grid-6 img {
                width: 16.66%;
                height: 16.66%;
            }

            .grid-9 img {
                width: 11.11%;
                height: 11.11%;
            }
        ''')
        output.append('</style>')

        if value:
            image_urls = value.split(',')
            num_images = len(image_urls)
            if num_images <= 4:
                grid_class = 'grid-4'
            elif num_images <= 6:
                grid_class = 'grid-6'
            else:
                grid_class = 'grid-9'

            for url in image_urls:
                output.append('<img src="{0}" class="admin-preview-image {1}" />'.format(url, grid_class))

        output.append(super().render(name, value, attrs, renderer))
        return mark_safe(''.join(output))


from django import forms
from django.utils.safestring import mark_safe
from xadmin.widgets import AdminTextareaWidget
# from xadmin.plugins.utils import vendor

class ImagePreviewPlugin(object):
    def __init__(self, field_name):
        self.field_name = field_name

    def get_readonly_fields(self, attrs=None):
        return [self.field_name]

    def get_form_field(self, form, field_name, init_value, **kwargs):
        if field_name == self.field_name:
            return form.field(
                field_name,
                widget=AdminTextareaWidget(attrs={'class': 'image-preview-widget', 'readonly': 'readonly'})
            )
        return form.formfield(**kwargs)

    def get_form_datas(self, datas):
        datas = datas.copy()
        if self.field_name in datas:
            urls = datas[self.field_name].split(',')
            urls_html = ''.join(f'<img src="{url}" alt="" />' for url in urls)
            datas[self.field_name] = mark_safe(urls_html)
        return datas

    def get_media(self, media):
        return media + vendor('xadmin.widget.select.js')

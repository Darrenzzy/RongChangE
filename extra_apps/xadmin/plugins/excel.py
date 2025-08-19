# -------------------------------
# -*- coding: utf-8 -*-
# @Author：jianghan
# @Time：2020/11/11 10:00
# @File: excel.py.py
# Python版本：3.6.8
# -------------------------------


import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader
from xadmin.plugins.utils import get_context_dict


# excel 导入
@xadmin.sites.register_plugin(ListAdminView)
class ListImportExcelPlugin(BaseAdminPlugin):
    import_excel = False
    # Excel 模板下载地址
    excel_template_uri = None

    # 入口函数, 通过此属性来指定此插件是否加载
    def init_request(self, *args, **kwargs):
        return bool(self.import_excel)

    # 如果加载, 则执行此函数添加一个导入字段
    def block_top_toolbar(self, context, nodes):
        ctx = get_context_dict(context)
        ctx['excel_template_uri'] = self.excel_template_uri
        nodes.append(loader.render_to_string('xadmin/blocks/model_list.top_toolbar.import.html',
                                             context=ctx))

from __future__ import absolute_import

from django.conf import settings

from xadmin.sites import register as xadmin_register
from xadmin.views import CommAdminView, BaseAdminView
from xadmin.layout import *

from django.utils.translation import gettext_lazy as _, gettext as ugettext

from .models import UserSettings, Log


@xadmin_register(UserSettings)
class UserSettingsAdmin(object):
    model_icon = 'fa fa-cog'
    hidden_menu = True


@xadmin_register(Log)
class LogAdmin(object):
    # remove_permissions = ["add", "change", "delete"]
    warnings_tip = True
    reversion_enable = False

    def link(self, instance):
        if instance.content_type and instance.object_id and instance.action_flag != 'delete':
            admin_url = self.get_admin_url(
                '%s_%s_change' % (instance.content_type.app_label, instance.content_type.model),
                instance.object_id)
            return "<a href='%s'>%s</a>" % (admin_url, _('Admin Object'))
        else:
            return ''

    link.short_description = ""
    link.allow_tags = True
    link.is_column = False

    list_display = ('action_time', 'user', 'ip_addr', 'content_type', 'action_flag', 'message', 'link')
    list_filter = ['user', 'action_time', 'action_flag', 'content_type__model', ]
    search_fields = ['ip_addr', 'message']
    model_icon = 'fa fa-cog'
    readonly_fields = ['data']

    def queryset(self):
        q = super().queryset()
        return q.select_related('user', "content_type")

    def has_add_permission(self, request=None, obj=None):
        return False

    def has_change_permission(self, request=None, obj=None):
        return False

    def has_delete_permission(self, request=None, obj=None):
        return False


@xadmin_register(BaseAdminView)
class BaseSetting:
    # 是否允许主题替换， 如果为 False 时不显示
    enable_themes = False
    # 企图调出主题菜单，显示更多主题
    use_bootswatch = False


# 后台管理页面的整体配置
@xadmin_register(CommAdminView)
class GlobalSetting:

    # 是否显示增加组件
    global_add_models = []
    # 是否显示搜索menu
    global_search_models = []

    menu_style = 'accordion'  # 'accordion' 可折叠，默认展开 default
    site_title = getattr(settings, "ADMIN_SITE_TITLE", 'django-xadmin')
    site_footer = getattr(settings, "ADMIN_SITE_FOOTER", 'django-xadmin')

    # xadmin-menu 排序，数值越大越靠前
    apps_label_order = {
        "modelname": 100,
    }

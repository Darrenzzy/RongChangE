# coding=utf-8
from django.db.models import Max

import reversion
from django import forms
from django.contrib.auth.forms import (UserCreationForm, UserChangeForm,
                                       AdminPasswordChangeForm, PasswordChangeForm)
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.utils.html import escape
from django.utils.encoding import smart_str as smart_text
from django.utils.translation import gettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.forms import ModelMultipleChoiceField
from django.contrib.auth import get_user_model
from xadmin.layout import Fieldset, Main, Side, Row, FormHelper
from xadmin.models import Log
from xadmin.sites import site
from xadmin.util import unquote
from xadmin.views import BaseAdminPlugin, ModelFormAdminView, ModelAdminView, CommAdminView, csrf_protect_m

User = get_user_model()

ACTION_NAME = {
    'add': _('Can add %s'),
    'change': _('Can change %s'),
    'edit': _('Can edit %s'),
    'delete': _('Can delete %s'),
    'view': _('Can view %s'),
    'export': _('导出: %s'),
}


def cache_orm_content_type(content_type_id: int) -> str:
    # https://docs.djangoproject.com/zh-hans/4.2/ref/settings/#caches
    local_cache = settings.CACHES.get("default", None)
    if local_cache is None:
        settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

    cache_name = "orm_ctx_type_query_result"

    result = cache.get(cache_name, {})
    if not result:
        result = {str(x.pk): x.app_labeled_name for x in ContentType.objects.all()}
        cache.set(cache_name, result, timeout=6)
    return result.get(str(content_type_id), "-")


def get_permission_name(p):
    action = p.codename.split('_')[0]
    if action in ACTION_NAME:
        # return ACTION_NAME[action] % str(p.content_type)
        return ACTION_NAME[action] % str(cache_orm_content_type(p.content_type_id))
    else:
        return p.name


class PermissionModelMultipleChoiceField(ModelMultipleChoiceField):

    def label_from_instance(self, p):
        return get_permission_name(p)


class GroupAdmin(object):
    search_fields = ('name',)
    ordering = ('name',)
    style_fields = {'permissions': 'm2m_transfer'}
    model_icon = 'fa fa-group'

    def get_field_attrs(self, db_field, **kwargs):
        attrs = super(GroupAdmin, self).get_field_attrs(db_field, **kwargs)
        if db_field.name == 'permissions':
            attrs['form_class'] = PermissionModelMultipleChoiceField
        return attrs


class UserAdmin(object):
    change_user_password_template = None
    list_display = (
        'username', 'first_name', 'groups', 'is_staff', 'email', 'last_login',
        'date_joined', 'get_update_at_time'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    # 'user_permissions': 'm2m_transfer',
    style_fields = {"groups": "m2m_transfer"}
    model_icon = 'fa fa-user'
    relfield_style = 'fk-ajax'
    exclude = ['user_permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ct = ContentType.objects.filter(app_label="auth", model="user").first()
        if ct:
            base = (
                Log.objects.filter(content_type_id=ct.pk, action_flag="change")
                .values("object_id").annotate(action_time=Max("action_time"))
            )
            self.update_query = {
                int(x['object_id']): x['action_time'].strftime("%Y年%m月%d日 %H:%M")
                for x in base
            }
        else:
            self.update_query = {}

    def queryset(self):
        q = super().queryset().prefetch_related('groups', )
        return q

    def get_update_at_time(self, obj):
        return self.update_query.get(obj.pk, obj.date_joined.strftime("%Y年%m月%d日 %H:%M"))

    get_update_at_time.short_description = "更新时间"
    get_update_at_time.is_column = True

    def get_field_attrs(self, db_field, **kwargs):
        attrs = super(UserAdmin, self).get_field_attrs(db_field, **kwargs)
        if db_field.name == 'user_permissions':
            attrs['form_class'] = PermissionModelMultipleChoiceField
        return attrs

    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            self.form = UserCreationForm
        else:
            self.form = UserChangeForm
        return super(UserAdmin, self).get_model_form(**kwargs)

    def get_form_layout(self):
        if self.org_obj:
            self.form_layout = (
                Main(
                    Fieldset('',
                             'username', 'password',
                             css_class='unsort no_title'
                             ),
                    Fieldset(_('Personal info'),
                             Row('first_name', 'last_name'),
                             'email'
                             ),
                    Fieldset(_('Permissions'),
                             'groups',
                             # 'user_permissions'
                             ),
                    Fieldset(_('Important dates'),
                             'last_login', 'date_joined'
                             ),
                ),
                Side(
                    Fieldset(_('Status'),
                             'is_active', 'is_staff', 'is_superuser',
                             ),
                )
            )
        return super(UserAdmin, self).get_form_layout()

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'groups':
            db_field.verbose_name = '角色'
        field = super().formfield_for_dbfield(db_field, **kwargs)
        return field


class PermissionAdmin(object):

    def queryset(self):
        q = super(PermissionAdmin, self).queryset()
        return q.select_related("content_type")

    def show_name(self, p):
        return get_permission_name(p)

    show_name.short_description = _('Permission Name')
    show_name.is_column = True

    model_icon = 'fa fa-lock'
    list_display = ('show_name', )


site.register(Group, GroupAdmin)
site.register(User, UserAdmin)
site.register(Permission, PermissionAdmin)
reversion.register()


class UserFieldPlugin(BaseAdminPlugin):

    user_fields = []

    def get_field_attrs(self, __, db_field, **kwargs):
        if self.user_fields and db_field.name in self.user_fields:
            return {'widget': forms.HiddenInput}
        return __()

    def get_form_datas(self, datas):
        if self.user_fields and 'data' in datas:
            if hasattr(datas['data'], '_mutable') and not datas['data']._mutable:
                datas['data'] = datas['data'].copy()
            for f in self.user_fields:
                datas['data'][f] = self.user.id
        return datas


site.register_plugin(UserFieldPlugin, ModelFormAdminView)


class ModelPermissionPlugin(BaseAdminPlugin):

    user_can_access_owned_objects_only = False
    user_owned_objects_field = 'user'

    def queryset(self, qs):
        if self.user_can_access_owned_objects_only and \
                not self.user.is_superuser:
            filters = {self.user_owned_objects_field: self.user}
            qs = qs.filter(**filters)
        return qs

    def get_list_display(self, list_display):
        if self.user_can_access_owned_objects_only and \
                not self.user.is_superuser and \
                self.user_owned_objects_field in list_display:
            list_display.remove(self.user_owned_objects_field)
        return list_display


site.register_plugin(ModelPermissionPlugin, ModelAdminView)


class AccountMenuPlugin(BaseAdminPlugin):

    def block_top_account_menu(self, context, nodes):
        return '<li><a href="%s"><i class="fa fa-key"></i> %s</a></li>' % (self.get_admin_url('account_password'), _('Change Password'))


site.register_plugin(AccountMenuPlugin, CommAdminView)


class ChangePasswordView(ModelAdminView):
    model = User
    change_password_form = AdminPasswordChangeForm
    change_user_password_template = None

    @csrf_protect_m
    def get(self, request, object_id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        self.obj = self.get_object(unquote(object_id))
        self.form = self.change_password_form(self.obj)

        return self.get_response()

    def get_media(self):
        media = super(ChangePasswordView, self).get_media()
        media = media + self.vendor('xadmin.form.css', 'xadmin.page.form.js') + self.form.media
        return media

    def get_context(self):
        context = super(ChangePasswordView, self).get_context()
        helper = FormHelper()
        helper.form_tag = False
        helper.include_media = False
        self.form.helper = helper
        context.update({
            'title': _('Change password: %s') % escape(smart_text(self.obj)),
            'form': self.form,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_view_permission': True,
            'original': self.obj,
        })
        return context

    def get_response(self):
        return TemplateResponse(self.request, [
            self.change_user_password_template or
            'xadmin/auth/user/change_password.html'
        ], self.get_context())

    @method_decorator(sensitive_post_parameters())
    @csrf_protect_m
    def post(self, request, object_id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        self.obj = self.get_object(unquote(object_id))
        self.form = self.change_password_form(self.obj, request.POST)

        if self.form.is_valid():
            self.form.save()
            self.message_user(_('Password changed successfully.'), 'success')
            return HttpResponseRedirect(self.model_admin_url('change', self.obj.pk))
        else:
            return self.get_response()


class ChangeAccountPasswordView(ChangePasswordView):
    change_password_form = PasswordChangeForm

    @csrf_protect_m
    def get(self, request):
        self.obj = self.user
        self.form = self.change_password_form(self.obj)

        return self.get_response()

    def get_context(self):
        context = super(ChangeAccountPasswordView, self).get_context()
        context.update({
            'title': _('Change password'),
            'account_view': True,
        })
        return context

    @method_decorator(sensitive_post_parameters())
    @csrf_protect_m
    def post(self, request):
        self.obj = self.user
        self.form = self.change_password_form(self.obj, request.POST)

        if self.form.is_valid():
            self.form.save()
            self.message_user(_('Password changed successfully.'), 'success')
            return HttpResponseRedirect(self.get_admin_url('index'))
        else:
            return self.get_response()


user_model = settings.AUTH_USER_MODEL.lower().replace('.', '/')
site.register_view(r'^%s/(.+)/password/$' % user_model,
                   ChangePasswordView, name='user_change_password')
site.register_view(r'^account/password/$', ChangeAccountPasswordView,
                   name='account_password')

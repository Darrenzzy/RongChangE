from collections import OrderedDict
from datetime import datetime
from io import BytesIO
# import urllib.parse as url_parse

from django import forms, VERSION as django_version
from django.core.exceptions import PermissionDenied
from django.db import router
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import loader
from django.template.response import TemplateResponse
import six
from django.utils.encoding import force_str as force_text, escape_uri_path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, ngettext as ungettext
from django.utils.text import capfirst

from django.contrib.admin.utils import get_deleted_objects

from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.util import model_format_dict, model_ngettext, get_obj_attr
from xadmin.views import BaseAdminPlugin, ListAdminView
from xadmin.views.base import filter_hook, ModelAdminView

from xadmin import views

import pandas as pd

ACTION_CHECKBOX_NAME = '_selected_action'
checkbox = forms.CheckboxInput({'class': 'action-select'}, lambda value: False)


def action_checkbox(obj):
    return checkbox.render(ACTION_CHECKBOX_NAME, force_text(obj.pk))


action_checkbox.short_description = mark_safe(
    '<input autocomplete="off" type="checkbox" id="action-toggle" />')
action_checkbox.allow_tags = True
action_checkbox.allow_export = False
action_checkbox.is_column = False


class BaseActionView(ModelAdminView):
    action_name = None
    description = None
    icon = 'fa fa-tasks'

    model_perm = 'change'

    @classmethod
    def has_perm(cls, list_view):
        return list_view.get_model_perms()[cls.model_perm]

    def init_action(self, list_view):
        self.list_view = list_view
        self.admin_site = list_view.admin_site

    @filter_hook
    def do_action(self, queryset):
        pass

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        if django_version > (2, 0):
            for model in self.admin_site._registry:
                if not hasattr(self.admin_site._registry[model], 'has_delete_permission'):
                    setattr(self.admin_site._registry[model], 'has_delete_permission', self.has_delete_permission)


class DeleteSelectedAction(BaseActionView):

    action_name = "delete_selected"
    description = _(u'Delete selected %(verbose_name_plural)s')

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    delete_models_batch = True

    model_perm = 'delete'
    icon = 'fa fa-times'

    @filter_hook
    def delete_models(self, queryset):
        n = queryset.count()
        if n:
            if self.delete_models_batch:
                self.log(
                    'delete',
                    _('Batch delete %(count)d %(items)s.') % {"count": n, "items": model_ngettext(self.opts, n)},
                    app_label=self.opts.app_label,
                    model_name=self.opts.model_name,
                    original_data=[get_obj_attr(obj) for obj in queryset],
                )
                queryset.delete()
            else:
                for obj in queryset:
                    self.log('delete', '成功删除 1 条数据.', obj, original_data=get_obj_attr(obj))
                    obj.delete()
            self.message_user(_("Successfully deleted %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(self.opts, n)
            }, 'success')

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_delete_permission():
            raise PermissionDenied

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.

        if django_version > (2, 1):
            deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
                queryset, self.opts, self.admin_site)
        else:
            using = router.db_for_write(self.model)
            deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
                queryset, self.opts, self.user, self.admin_site, using)


        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if perms_needed:
                raise PermissionDenied
            self.delete_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)

        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": objects_name}
        else:
            title = _("Are you sure?")

        context = self.get_context()
        context.update({
            "title": title,
            "objects_name": objects_name,
            "deletable_objects": [deletable_objects],
            'queryset': queryset,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        })

        # Display the confirmation page
        return TemplateResponse(self.request, self.delete_selected_confirmation_template or
                                self.get_template_list('views/model_delete_selected_confirm.html'), context)


class ActionPlugin(BaseAdminPlugin):

    # Actions
    actions = []
    actions_selection_counter = True
    global_actions = [DeleteSelectedAction]

    def init_request(self, *args, **kwargs):
        self.actions = self.get_actions()
        return bool(self.actions)

    def get_list_display(self, list_display):
        if self.actions:
            list_display.insert(0, 'action_checkbox')
            self.admin_view.action_checkbox = action_checkbox
        return list_display

    def get_list_display_links(self, list_display_links):
        if self.actions:
            if len(list_display_links) == 1 and list_display_links[0] == 'action_checkbox':
                return list(self.admin_view.list_display[1:2])
        return list_display_links

    def get_context(self, context):
        if self.actions and self.admin_view.result_count:
            av = self.admin_view
            selection_note_all = ungettext('%(total_count)s selected',
                                           'All %(total_count)s selected', av.result_count)

            new_context = {
                'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(av.result_list)},
                'selection_note_all': selection_note_all % {'total_count': av.result_count},
                'action_choices': self.get_action_choices(),
                'actions_selection_counter': self.actions_selection_counter,
            }
            context.update(new_context)
        return context

    def post_response(self, response, *args, **kwargs):
        request = self.admin_view.request
        av = self.admin_view

        # Actions with no confirmation
        if self.actions and 'action' in request.POST:
            action = request.POST['action']

            if action not in self.actions:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                av.message_user(msg)
            else:
                ac, name, description, icon = self.actions[action]
                select_across = request.POST.get('select_across', False) == '1'
                selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

                if not selected and not select_across:
                    # Reminder that something needs to be selected or nothing will happen
                    msg = _("Items must be selected in order to perform "
                            "actions on them. No items have been changed.")
                    av.message_user(msg)
                else:
                    queryset = av.list_queryset._clone()
                    if not select_across:
                        # Perform the action only on the selected objects
                        queryset = av.list_queryset.filter(pk__in=selected)
                    response = self.response_action(ac, queryset)
                    # Actions may return an HttpResponse, which will be used as the
                    # response from the POST. If not, we'll be a good little HTTP
                    # citizen and redirect back to the changelist page.
                    if isinstance(response, HttpResponse):
                        return response
                    else:
                        return HttpResponseRedirect(request.get_full_path())
        return response

    def response_action(self, ac, queryset):
        if isinstance(ac, type) and issubclass(ac, BaseActionView):
            action_view = self.get_model_view(ac, self.admin_view.model)
            action_view.init_action(self.admin_view)
            return action_view.do_action(queryset)
        else:
            return ac(self.admin_view, self.request, queryset)

    def get_actions(self):
        if self.actions is None:
            return OrderedDict()

        actions = [self.get_action(action) for action in self.global_actions]

        for klass in self.admin_view.__class__.mro()[::-1]:
            class_actions = getattr(klass, 'actions', [])
            if not class_actions:
                continue
            actions.extend(
                [self.get_action(action) for action in class_actions])

        # get_action might have returned None, so filter any of those out.
        actions = filter(None, actions)
        if six.PY3:
            actions = list(actions)

        # Convert the actions into a OrderedDict keyed by name.
        actions = OrderedDict([
            (name, (ac, name, desc, icon))
            for ac, name, desc, icon in actions
        ])

        return actions

    def get_action_choices(self):
        """
        Return a list of choices for use in a form object.  Each choice is a
        tuple (name, description).
        """
        choices = []
        for ac, name, description, icon in self.actions.values():
            choice = (name, description % model_format_dict(self.opts), icon)
            choices.append(choice)
        return choices

    def get_action(self, action):
        if isinstance(action, type) and issubclass(action, BaseActionView):
            if not action.has_perm(self.admin_view):
                return None
            return action, getattr(action, 'action_name'), getattr(action, 'description'), getattr(action, 'icon')

        elif callable(action):
            func = action
            action = action.__name__

        elif hasattr(self.admin_view.__class__, action):
            func = getattr(self.admin_view.__class__, action)

        else:
            return None

        if hasattr(func, 'short_description'):
            description = func.short_description
        else:
            description = capfirst(action.replace('_', ' '))

        return func, action, description, getattr(func, 'icon', 'tasks')

    # View Methods
    def result_header(self, item, field_name, row):
        if hasattr(item, "attr") and field_name == 'action_checkbox':
            item.classes.append("action-checkbox-column")
        return item

    def result_item(self, item, obj, field_name, row):
        if item.field is None and field_name == u'action_checkbox':
            item.classes.append("action-checkbox")
        return item

    # Media
    def get_media(self, media):
        if self.actions and self.admin_view.result_count:
            media = media + self.vendor('xadmin.plugin.actions.js', 'xadmin.plugins.css')
        return media

    # Block Views
    def block_results_bottom(self, context, nodes):
        if self.actions and self.admin_view.result_count:
            nodes.append(loader.render_to_string('xadmin/blocks/model_list.results_bottom.actions.html',
                                                 context=get_context_dict(context)))


site.register_plugin(ActionPlugin, ListAdminView)


# 自定义 download action
def generate_excel_bytes(df: pd.DataFrame, sheet_name: str):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False, freeze_panes=(1, 0))
    return buf


def get_file_stream_response(buf, filename):
    response = StreamingHttpResponse(buf, content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = "attachment;filename=%s.xlsx" % escape_uri_path(
        f"{filename}-{datetime.now().strftime('%Y%m%d%H%M%f')}")
    return response


class CustomDownAction(BaseActionView):
    action_name = u"批量导出表格数据"  #: 相当于这个 Action 的唯一标示, 尽量用比较针对性的名字
    model_perm = 'export'  #: 该 Action 所需权限
    description = _(u'批量导出表格数据 %(verbose_name_plural)s')
    icon = 'fa fa-download'

    # 实现到处数据的查询， return pandas.DataFrame, table_header: map, file_name: str
    to_download = None

    warnings_tip = True
    warnings_str = '''
        您访问的系统包含系统秘密数据，请确保您的行为包括数据访问、修改和共享都符合《中华人民共和国网络安全法》和任何同等法规。
        如果您没有访问系统秘密数据的权限，请立即终止您的登录。
        '''

    # @filter_hook
    def do_action(self, queryset):
        if not callable(self.to_download):
            raise NotImplementedError(
                "需要实现 to_download 方法，该方法返回导出数据的pandas DataFrame & sheet-name 文件名称")
        if not self.has_change_permission():
            raise PermissionDenied

        if self.request.POST.get('download_ai'):
            return self.do_download_action(queryset)

        _count = queryset.count()
        if _count == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)

        title = _("Are you sure?")
        context = self.get_context()
        context.update({
            "title": title,
            "objects_name": objects_name,
            'count': _count,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            'queryset': queryset.values_list("pk", flat=True),
            "warnings_tip": self.warnings_tip,
            "warnings_str": self.warnings_str,
            "cancel_link": self.request.build_absolute_uri(),
        })

        # Display the confirmation page
        return TemplateResponse(self.request,
                                self.get_template_list('views/model_do_download_confirm.html'),
                                context)

    def do_download_action(self, queryset):
        """
        下载 imp
        """

        sheet_name = "sheet-1"
        df, file_name = self.to_download(queryset)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        file_name = "后台导出{}-{}".format(file_name, datetime.now().strftime('%Y-%m-%d%H:%M:%S'))
        response["Content-Disposition"] = 'attachment;filename={0}.xlsx'.format(escape_uri_path(file_name))

        # data_length = df.size
        data_length = len(df)
        if data_length == 0:
            # raise Exception("暂无数据")
            outfile = BytesIO()
            df.to_excel(outfile, index=False)
            response.write(outfile.getvalue())
            return response

        response.write(generate_excel_bytes(df, sheet_name).getvalue())
        self.log(
            flag="export",
            message="导出 %s %s格式 %s条数据" % (file_name, "xlsx", data_length),
            app_label=self.opts.app_label,
            model_name=self.opts.model_name,
            object_repr="数据导出记录",
        )
        return response

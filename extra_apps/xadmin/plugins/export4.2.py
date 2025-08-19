import io
import datetime
import pandas
from django.contrib import messages
from future.utils import iteritems
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.encoding import force_str, smart_str
from datetime import datetime
from django.utils.translation import gettext as _
from django.db.models import ForeignKey
from django.contrib.admin.utils import label_for_field
from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView, ExportAdminView
from xadmin.views.list import ALL_VAR
from xadmin.filters import FILTER_PREFIX


class ExportMenuPlugin(BaseAdminPlugin):

    list_export = ('xlsx', 'csv', 'xml', 'json')
    export_names = {
        'xlsx': 'Excel',
        'csv': 'CSV',
        'xml': 'XML',
        'json': 'JSON'
    }
    # 数据导出警告
    warnings_tip = False
    # 警告话术
    warnings_str = '''
    您访问的系统包含系统秘密数据，请确保您的行为包括数据访问、修改和共享都符合《中华人民共和国网络安全法》和任何同等法规。
    如果您没有访问系统秘密数据的权限，请立即终止您的登录。
    '''

    def init_request(self, *args, **kwargs):
        return self.list_export

    def block_top_toolbar(self, context, nodes):
        if self.list_export:
            context.update({
                'previous_url': context['request'].build_absolute_uri(),
                'export_url': self.admin_view.model_admin_url('export'),
                'show_export_all': self.admin_view.paginator.count > self.admin_view.list_per_page and not ALL_VAR in self.admin_view.request.GET,
                'form_params': self.admin_view.get_form_params({'_do_': 'export'}, ('export_type',)),
                'export_types': [{'type': et, 'name': self.export_names[et]} for et in self.list_export],
                "warnings_tip": self.warnings_tip,
                "warnings_str": self.warnings_str or "敏感信息导出请慎重，勿泄漏",
            })
            nodes.append(loader.render_to_string('xadmin/blocks/model_list.top_toolbar.exports.html',
                                                 context=get_context_dict(context)))


class ExportPlugin(BaseAdminPlugin):

    export_mimes = {
        'xlsx': 'application/vnd.ms-excel',
        'csv': 'text/csv',
        'xml': 'application/xhtml+xml',
        'json': 'application/json'
    }
    export_fields = '__all__'

    def init_request(self, *args, **kwargs):
        return self.request.POST.get('_do_') == 'export'

    def _get_headers(self, field_name, model):
        try:
            return label_for_field(field_name, model)
        except AttributeError:
            parts = field_name.split('__', 1)
            field = model._meta.get_field(parts[0])
            if isinstance(field, ForeignKey):
                return self._get_headers(parts[1], field.related_model)
            raise

    def get_export_fields(self):
        export_fields = []
        if self.export_fields == '__all__':
            for field in self.admin_view.opts.fields:
                export_fields.append(field.name)
            return export_fields
        return self.export_fields

    def get_export_choice_fields(self):
        export_fields = {}
        if self.export_fields == '__all__':
            for field in self.admin_view.opts.fields:
                if hasattr(field, 'choices') and field.choices:
                    export_fields[field.verbose_name] = {key: value for key, value in field.choices}
                # if isinstance(field, ForeignKey):
                #     print(f"field = {type(field), field.__dict__}")
                #     # export_fields[field.verbose_name] = {getattr(field, field.to_fields[0]): field.__str__()}
                #     export_fields[field.verbose_name] = {field.related_model.pk: str(field.related_model)}
        return export_fields

    def _get_datas(self):
        query_params = {}
        for k, v in self.request.POST.items():
            if k.startswith(FILTER_PREFIX):
                name = k.replace(FILTER_PREFIX, '')
                query_params[name] = v

        export_fields = self.get_export_fields()
        queryset = self.admin_view.queryset().filter(**query_params).values_list(*export_fields)
        columns = [self._get_headers(field_name, self.admin_view.model) for field_name in export_fields]

        if self.request.POST.get('all', 'off') == 'on':
            df = pandas.DataFrame(queryset, columns=columns)
            export_field_choice_map = self.get_export_choice_fields()
            print(f"columns={columns}")
            print(f"export_field_choice_map={export_field_choice_map}")
            if export_field_choice_map:
                for _choice, _map in export_field_choice_map.items():
                    if _choice in columns:
                        df[_choice] = df[_choice].map(_map)
        else:
            df = pandas.DataFrame([], columns=columns)
        return df

    # def _get_datas(self):
    #     rows = context['results']
    #
    #     new_rows = [[self._format_value(o) for o in
    #                  filter(lambda c: getattr(c, 'export', False), r.cells)] for r in rows]
    #     new_rows.insert(0, [force_str(c.text) for c in context['result_headers'].cells if c.export])
    #     return pandas.DataFrame(new_rows)

    def get_xlsx_export(self):
        datas: pandas.DataFrame = self._get_datas()
        output = io.BytesIO()
        model_name = self.opts.verbose_name
        export_header = self.request.POST.get('export_xlsx_header', 'off') == 'on'

        with pandas.ExcelWriter(output, engine='xlsxwriter', datetime_format='yyyy年mm月dd日 HH:MM') as writer:
            datas.to_excel(writer, index=False, sheet_name=force_str(model_name), header=export_header)

        output.seek(0)
        return output.getvalue()

    def get_csv_export(self):
        datas = self._get_datas()
        export_header = self.request.POST.get('export_csv_header', 'off') == 'on'
        return datas.to_csv(index=False, header=export_header)

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement("row", {})
                self._to_xml(xml, item)
                xml.endElement("row")
        elif isinstance(data, dict):
            for key, value in iteritems(data):
                key = key.replace(' ', '_')
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)
        else:
            xml.characters(smart_str(data))

    def get_xml_export(self):
        datas = self._get_datas()
        return datas.to_xml(index=False)

    def get_json_export(self):
        datas = self._get_datas()
        return datas.to_json(orient='table', index=False, date_unit='s', force_ascii=False, indent=4)

    def get_response(self, response, context, *args, **kwargs):
        print(f"get_response context={context}")
        return super().get_response(response, context, *args, **kwargs)

    def post_response(self):
        print(f"self={self.__dict__}")
        file_type = self.request.POST.get('export_type', "")
        print(f"file_type={file_type}")
        if file_type is None or not self.export_mimes.get(file_type, False):
            messages.add_message(self.request, messages.ERROR, "文件导出类型异常")
            return HttpResponseRedirect(self.request.path)

        response = HttpResponse(
            content_type="%s; charset=utf8" % self.export_mimes[file_type]
        )

        file_name = f'{self.opts.verbose_name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d%H%M")}'
        response['Content-Disposition'] = ('attachment; filename=%s.%s' % (
            file_name, file_type)).encode('utf-8')

        try:
            response.write(getattr(self, 'get_%s_export' % file_type)())
            self.log(
                flag="export",
                message="导出 %s %s格式 数据" % (file_name, file_type),
                app_label=self.opts.app_label,
                model_name=self.opts.model_name,
                object_repr="数据导出记录",
            )
            return response
        except Exception as ex:
            self.message_user(f'导出失败！原因：{ex}', level='error')
            return self.request.POST.get('previous_url') or self.request.build_absolute_uri()


site.register_plugin(ExportMenuPlugin, ListAdminView)
site.register_plugin(ExportPlugin, ExportAdminView)

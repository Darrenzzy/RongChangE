### 适配升级django4.2

* 涉及批量替换相关包引用函数、django4.2 已废弃函数
```text
from django.utils.encoding import force_text
from django.utils.encoding import force_str as force_text


from django.utils.translation import ugettext as _, ungettext
from django.utils.translation import gettext as _, ngettext as ungettext


from django.utils.translation import ugettext as _
from django.utils.translation import gettext as _


xadmin/plugin/ajax.py:
	BaseAjaxPlugin.init_request
		- return bool(self.request.is_ajax() or self.request.GET.get('_ajax'))
		- return bool(self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or self.request.GET.get('_ajax'))


xadmin/plugin/auth.py:
	def get_permission_name(p)
		- 新增优化，将原有的content-type表由遍历调整为整表查询集缓存，空间换时间。
		- 请见代码块 def cache_orm_content_type(content_type_id: int) -> str
		
		
xadmin/plugin/editable.py:	
xadmin/plugin/chart.py:	
	label_for_field 函数将由 django.contrib.admin.utils 提供，而非xadmin
		- from xadmin.util import lookup_field, label_for_field, json
		- from django.contrib.admin.utils import label_for_field


xadmin/plugin/filters.py:	
	lookup_needs_distinct 函数将由  lookup_spawns_duplicates 实现
		- from django.contrib.admin.utils import get_fields_from_path, lookup_needs_distinct
		- from django.contrib.admin.utils import get_fields_from_path, lookup_spawns_duplicates


xadmin/plugin/importexport.py:
	新版本的djangoimportexport SKIP_ADMIN_LOG, TMP_STORAGE_CLASS 将废弃，由ImportMixin, ImportExportMixinBase取代
		- from import_export.admin import DEFAULT_FORMATS, SKIP_ADMIN_LOG, TMP_STORAGE_CLASS
		- from import_export.admin import DEFAULT_FORMATS, ImportMixin, ImportExportMixinBase
	
	class ImportBaseView(ModelAdminView) 内get_skip_admin_log和get_tmp_storage_class函数将发生变化
		- get_skip_admin_log.return SKIP_ADMIN_LOG -> get_skip_admin_log.return ImportMixin(ImportExportMixinBase).get_skip_admin_log()
		- get_tmp_storage_class.return TMP_STORAGE_CLASS -> get_skip_admin_log.return ImportMixin(ImportExportMixinBase).get_tmp_storage_class()
		
		
xadmin/plugin/layout.py:
	label_for_field 函数将由 django.contrib.admin.utils 提供，而非xadmin 
		- from xadmin.util import label_for_field
		- from django.contrib.admin.utils import label_for_field
		
		
xadmin/plugin/wizard.py:
xadmin/plugin/quickform.py:
	is_ajax 函数在django4.2废弃
		- WizardFormPlugin.init_request self.request.is_ajax() -> self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
		- QuickFormPlugin.init_request self.request.is_ajax() -> self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
		
		
xadmin/templates/xadmin/includes/pagination.html:
	由于升级高版本 crispy_forms, ifequal - > if a == b , endifequal -> endif 
		-   <li><span><span class="text-success">{{ cl.result_count }}</span> {% ifequal cl.result_count 1 %}{{ cl.opts.verbose_name }}{% else %}{{ cl.opts.verbose_name_plural }}{% endifequal %}</span></li>
		-   <li><span><span class="text-success">{{ cl.result_count }}</span> {% if cl.result_count == 1 %}{{ cl.opts.verbose_name }}{% else %}{{ cl.opts.verbose_name_plural }}{% endif %}</span></li>


xadmin/views/detail.py
	ShowField.render()  函数由于升级高版本 crispy_forms ，导致函数签名变化，不一致，新版本取消了 form_style 字段。
		-     def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
					super(ShowField, self).render(form, form_style, context, template_pack, extra_context, **kwargs)
		-     def render(self, form, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
					super(ShowField, self).render(form, context, template_pack, extra_context, **kwargs)

        
xadmin/views/edit.py
	ModelFormAdminView.get_form_layout函数， 由于升级高版本 crispy_forms， get_form_layout函数返回取值问题。
	# crispy_forms 版本1.9.2时期 layout.get_field_names() 可以采用下述方式取值
    # rendered_fields = [i[1] for i in layout.get_field_names()]
    # crispy_forms 2.0 以后以下方式
    # rendered_fields = [i.name for i in layout.get_field_names()]
			
		- rendered_fields = [i[1] for i in layout.get_field_names()]
		- rendered_fields = [i.name for i in layout.get_field_names()]
		
	
xadmin/forms.py
	never_cache 在django4.2上追加属性判断，导致xadmin使用直接报错，故此采用在xadmin上使用上个版本的该函数的实现 
		- from django.views.decorators.cache import never_cache
		- from xadmin.patch_tools import never_cache
		

xadmin/sites.py
	AdminSite.check_dependencies 函数中的 if not ContentType._meta.installed: 判断，django4.2废弃 installed 函数，调整为自己实现这个判断
		- if not ContentType._meta.installed:
		- if ContentType._meta.app_config is None:


xadmin/util.py
	def boolean_icon(field_val) 修改该函数的KeyError问题
	
```

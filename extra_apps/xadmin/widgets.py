"""
Form Widget classes specific to the Django admin site.
"""
from __future__ import absolute_import
from itertools import chain
from django import forms
from django.template.loader import render_to_string

try:
    from django.forms.widgets import ChoiceWidget as RadioChoiceInput, Select, ChoiceWidget
except:
    from django.forms.widgets import RadioFieldRenderer, RadioChoiceInput
from django.utils.encoding import force_str as force_text

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape, format_html
from django.utils.translation import gettext as _

from .util import vendor


class AdminDateWidget(forms.DateInput):

    @property
    def media(self):
        return vendor('datepicker.js', 'datepicker.css', 'xadmin.widget.datetime.js')

    def __init__(self, attrs=None, format=None):
        final_attrs = {'autocomplete': 'off', 'class': 'date-field form-control', 'size': '10'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminDateWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super(AdminDateWidget, self).render(name, value, attrs, renderer)
        return mark_safe('<div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                         '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>' % (input_html, _(u'Today')))


class AdminTimeWidget(forms.TimeInput):

    @property
    def media(self):
        return vendor('datepicker.js', 'clockpicker.js', 'clockpicker.css', 'xadmin.widget.datetime.js')

    def __init__(self, attrs=None, format=None):
        final_attrs = {'autocomplete': 'off', 'class': 'time-field form-control', 'size': '8'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTimeWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super(AdminTimeWidget, self).render(name, value, attrs, renderer)
        return mark_safe('<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                         '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>' % (input_html, _(u'Now')))


class AdminSelectWidget(forms.Select):

    @property
    def media(self):
        return vendor('select.js', 'select.css', 'xadmin.widget.select.js')


class AdminSplitDateTime(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """

    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, AdminTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, widgets, attrs)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = [ht for ht in super(AdminSplitDateTime, self).render(name, value, attrs, renderer).replace('><input', '>\n<input').split('\n') if ht != '']
        # return input_html
        return mark_safe('<div class="datetime clearfix"><div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                         '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>'
                         '<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                         '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div></div>' % (input_html[0], _(u'Today'), input_html[1], _(u'Now')))

    def format_output(self, rendered_widgets):
        return mark_safe(u'<div class="datetime clearfix">%s%s</div>' %
                         (rendered_widgets[0], rendered_widgets[1]))


class AdminRadioInput(RadioChoiceInput):

    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        attrs['class'] = attrs.get('class', '').replace('form-control', '')
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_text(self.choice_label))
        if attrs.get('inline', False):
            return mark_safe(u'<label%s class="radio-inline">%s %s</label>' % (label_for, self.tag(), choice_label))
        else:
            return mark_safe(u'<div class="radio"><label%s>%s %s</label></div>' % (label_for, self.tag(), choice_label))


class AdminRadioFieldRenderer(forms.RadioSelect):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield AdminRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]  # Let the IndexError propogate
        return AdminRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)

    def render(self):
        return mark_safe(u'\n'.join([force_text(w) for w in self]))


class AdminRadioSelect(forms.RadioSelect):
    renderer = AdminRadioFieldRenderer


class AdminCheckboxSelect(forms.CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=(), renderer=None):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        output = []
        # Normalize to strings
        str_values = set([force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_text(option_label))

            if final_attrs.get('inline', False):
                output.append(u'<label%s class="checkbox-inline">%s %s</label>' % (label_for, rendered_cb, option_label))
            else:
                output.append(u'<div class="checkbox"><label%s>%s %s</label></div>' % (label_for, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))


class AdminSelectMultiple(forms.SelectMultiple):

    def __init__(self, attrs=None):
        final_attrs = {'autocomplete': 'off', 'class': 'select-multi'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminSelectMultiple, self).__init__(attrs=final_attrs)


class AdminFileWidget(forms.ClearableFileInput):
    template_with_initial = (u'<p class="file-upload">%s</p>'
                             % forms.ClearableFileInput.initial_text)
    template_with_clear = (u'<span class="clearable-file-input">%s</span>'
                           % forms.ClearableFileInput.clear_checkbox_label)


class AdminTextareaWidget(forms.Textarea):

    def __init__(self, attrs=None):
        final_attrs = {'autocomplete': 'off', 'class': 'textarea-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTextareaWidget, self).__init__(attrs=final_attrs)


class AdminTextInputWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'autocomplete': 'off', 'class': 'text-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTextInputWidget, self).__init__(attrs=final_attrs)


class AdminURLFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'autocomplete': 'off', 'class': 'url-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminURLFieldWidget, self).__init__(attrs=final_attrs)


class AdminIntegerFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'autocomplete': 'off', 'class': 'int-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminIntegerFieldWidget, self).__init__(attrs=final_attrs)


class AdminCommaSeparatedIntegerFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'autocomplete': 'off', 'class': 'sep-int-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminCommaSeparatedIntegerFieldWidget,
              self).__init__(attrs=final_attrs)


class ManyFilterWidget(forms.Select):

    # media方法是引入你所需要的js、css文件
    @property
    def media(self):
        # 共四个文件：bootstrap.min.css  jquery-1.11.0.min.js  selectpage.css selectpage.js，前两个系统已经加载，只需再加载后两个
        return vendor('xadmin.widget.selectpage.js', 'xadmin.widget.selectpage.css')

    # render方法是渲染你要展示字段的样式，通常返回html字符串
    def render(self, name, value, attrs=None, renderer=None):
        # 将数据库中已经被选中的值展示到页面，要将value（[1,3,5,8...]列表格式）转化为value_str（‘1,3,5,8’字符串格式）
        value_str = ','.join(map(str, value)) if value else ''

        # 可以用self.attrs获取之前传递的request相关的参数
        attrs = self.attrs

        # 获取多对多字段的所有可选选项传递到前端，以便前端进行搜索过滤
        choices = self.choices.field._queryset
        # choices_data格式固定
        choices_data = [{'id': choice.id, 'name': choice.username} for choice in choices]
        return mark_safe('<div >'
                         '<div class="manyfilter" id="m2m_%s" style="display: none">%s</div>'
                         '<div class="col-md-12" style="padding:0">'
                         '<input type="text" id="selectPage_%s" class="form-control" name="%s" value=%s placeholder="请输入查询关键字">'
                         '</div>'
                         '</div>'
                         % (name, choices_data, name, name, value_str))


class APIAutocompleteWidget(AdminTextInputWidget):
    def __init__(self, attrs=None, api_url=None, *args, **kwargs):
        self.api_url = api_url
        super().__init__(attrs, *args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['api_url'] = self.api_url
        return context

    # class Media:
    #     css = {
    #         'all': ['https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css'],
    #     }
    #     js = [
    #         'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js',
    #     ]

    @property
    def media(self):
        return vendor('select2.min.css', 'select2.min.js')


class Select2Mixin:
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'select2'
        output = super().render(name, value, attrs, renderer)
        return format_html('<div class="select2-container">{}</div>', output)

    # class Media:
    #     css = {
    #         'all': ['https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css'],
    #     }
    #     js = [
    #         'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js',
    #     ]

    @property
    def media(self):
        return vendor('select2.min.css', 'select2.min.js')


class Select2Select(Select2Mixin, Select):
    pass


class AdminRemoteSelectWidget(forms.Select):
    def __init__(self, api_uri: str = None, attrs=None, *args, **kwargs):
        # 当前 api-uri 需要支持模糊过滤  和 pk 精确检索功能
        # 返回格式：
        # 1. { "list":[  {"id": 1, "name": ""}, {}, ... ] }
        # 2. { "data":{ "id": 1, "name": "" }}
        self.api_uri = api_uri
        super().__init__(attrs, *args, **kwargs)

    @property
    def media(self):
        return vendor('select.js', 'select.css', 'xadmin.widget.select.js')

    def render(self, name, value, attrs=None, renderer=None):
        # render方法是渲染你要展示字段的样式，通常返回html字符串
        # 将数据库中已经被选中的值展示到页面，要将value（[1,3,5,8...]列表格式）转化为value_str（‘1,3,5,8’字符串格式）

        # value_str = value

        # 可以用self.attrs获取之前传递的request相关的参数

        # attrs = self.attrs
        # final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})

        # 获取多对多字段的所有可选选项传递到前端，以便前端进行搜索过滤

        # choices = self.choices.field._queryset

        # choices_data格式固定
        # print(choices)
        # choices_data = [{'id': choice.id, 'name': choice.name} for choice in choices]

        return mark_safe(
            render_to_string("xadmin/remote_select.html", {"name": name, "value": value, "api_uri": self.api_uri})
        )


class AdminCheckboxFormWidget(forms.CheckboxInput):
    def __init__(self, attrs=None, check_test=None):
        super().__init__(attrs=attrs, check_test=check_test)

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        print(f'className={self.__class__.__name__}, name={name}, value={value}')
        print(f'context={context}')
        return self._render(self.template_name, context, renderer)

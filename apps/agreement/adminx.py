from agreement.models import PrivacyPolicy, LaborFeeLevel
from xadmin.sites import register
from xadmin.views.base import csrf_protect_m
from django.db import transaction
from django.core.cache import cache
from django.core.exceptions import ValidationError


@register(PrivacyPolicy)
class PrivacyPolicyAdmin(object):
    list_display = ['title', 'state', 'created_at']
    list_filter = ['state', 'created_at']
    search_fields = ['title']
    remove_permissions = ['delete']
    style_fields = {
        'content': 'ueditor'
    }

    def save_models(self):
        super().save_models()
        if self.org_obj:
            # update
            if self.new_obj.state == self.model.ACTIVE:
                if 'state' in self.form_obj.changed_data:
                    # 修改了当前激活状态的手册
                    self.model.objects.exclude(pk=self.new_obj.pk).update(state=self.model.DEACTIVE)
                    return cache.set('agreement:privacyPolicy:active', self.new_obj.content, timeout=None)
                if 'content' in self.form_obj.changed_data:
                    # 更新了激活状态的手册内容
                    return cache.set('agreement:privacyPolicy:active', self.new_obj.content, timeout=None)
        else:
            # create
            if self.new_obj.state == self.model.ACTIVE:
                return cache.set('agreement:operatingManual:active', self.new_obj.content, timeout=None)


@register(LaborFeeLevel)
class LaborFeeLevelAdmin(object):
    list_display = ['id', 'level', 'state', 'remark', 'created_at']
    list_filter = ['state', 'created_at']
    list_editable = ['state']
    remove_permissions = ['delete']

    def save_models(self):
        if self.org_obj and 'level' in self.form_obj.changed_data:
            raise ValidationError('不允许修改档位值')
        super().save_models()
        cache.set(f'agreement:feeLevel:{self.new_obj.pk}', self.new_obj.level, timeout=None)

    @csrf_protect_m
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ValidationError as exc:
            self.form_obj.add_error(exc.params, exc)
            return self.get_response()

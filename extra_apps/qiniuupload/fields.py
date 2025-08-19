from django import forms
from django.conf import settings

from django.db import models

from qiniuupload.qiniuupload import QiniuUploader


class QiniuField(models.CharField):

    def __init__(self, *args, **kwargs):
        self.config_name = kwargs.pop("config_name", "default")
        self.extra_plugins = kwargs.pop("extra_plugins", [])
        self.external_plugin_resources = kwargs.pop("external_plugin_resources", [])
        # 上传 pre-location
        self.upload_to = kwargs.pop("upload_to", "media/")
        super(QiniuField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'upload_to': self.upload_to,
            'form_class': self._get_form_class(),
            'config_name': self.config_name,
            'extra_plugins': self.extra_plugins,
            'external_plugin_resources': self.external_plugin_resources
        }
        defaults.update(kwargs)
        return super(QiniuField, self).formfield(**defaults)

    @staticmethod
    def _get_form_class():
        return QiniuFileFormField

    def urls(self):
        # print(f"__dict__ = {self.__dict__}")
        return f"{settings.QINIU_DOMAIN}/{self.name}"


class QiniuFileFormField(forms.fields.CharField):

    def __init__(
            self,
            upload_to='media/',
            config_name='default',
            extra_plugins=None,
            external_plugin_resources=None,
            *args,
            **kwargs
    ):
        kwargs.update(
            {
                'widget': QiniuUploader(
                    upload_to=upload_to,
                    config_name=config_name,
                    extra_plugins=extra_plugins,
                    external_plugin_resources=external_plugin_resources
                )
            }
        )
        super(QiniuFileFormField, self).__init__(*args, **kwargs)

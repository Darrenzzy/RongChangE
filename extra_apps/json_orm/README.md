### orm json field

* 在x-admin页面上形成 json 校验以及 json 美化展示效果
* 本质上是  Text, 非专业数据库 json 字段, 慎重
* demo

```python
from django.db import models
from json_orm.fields import JSONField


class Cfg(models.Model):
    """
    配置表
    """

    title = models.CharField(verbose_name="key", max_length=50, unique=True)
    values = JSONField(verbose_name="values", help_text="json格式数据支持")

    expire = models.DateTimeField(verbose_name='失效时间', null=True, blank=True,
                                  help_text="若想永久有效请将失效时间为空")

    time_update = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    time_create = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        verbose_name = "配置表"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return str(self.title)
```

from utils.models import BaseModel
from DjangoUeditor.models import UEditorField
from user.models import Doctor
from django.db import models
import reversion


@reversion.register
class PrivacyPolicy(BaseModel):
    ACTIVE = 1
    DEACTIVE = 2
    STATE_CHOICES = (
        (ACTIVE, '激活'),
        (DEACTIVE, '禁用')
    )

    title = models.CharField(max_length=64, verbose_name='条款名称', db_comment='条款名称')
    content = UEditorField(verbose_name='条款正文', db_comment='条款正文')
    state = models.PositiveIntegerField(
        choices=STATE_CHOICES, default=ACTIVE, verbose_name='条款状态', db_comment='条款状态'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pk']
        verbose_name = '隐私条款'
        verbose_name_plural = verbose_name


@reversion.register
class LaborFeeLevel(BaseModel):
    ACTIVE = 1
    DEACTIVE = 2

    STATE_CHOICES = (
        (ACTIVE, '激活'),
        (DEACTIVE, '禁用')
    )

    level = models.PositiveIntegerField(verbose_name='档位', db_comment='档位')
    remark = models.CharField(
        max_length=32, null=True, blank=True, verbose_name='备注', db_comment='备注'
    )
    state = models.PositiveSmallIntegerField(
        choices=STATE_CHOICES, default=ACTIVE, verbose_name='状态', db_comment='状态'
    )

    def __str__(self):
        return f'{self.get_state_display()}-{self.level}'

    class Meta:
        ordering = ['level']
        verbose_name = '劳务费档位'
        verbose_name_plural = verbose_name

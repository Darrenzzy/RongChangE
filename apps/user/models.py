from django.db import models
from utils.models import BaseModel
import reversion
from xadmin.expand_model_fields import EncryptedCharField


@reversion.register
class Doctor(BaseModel):
    STATE_CHOICES = ((0, "初始化"), (1, "待审核"), (2, "已认证"), (3, "不通过"))

    openid = models.CharField(
        max_length=128, null=True, editable=False, verbose_name='微信openid', db_comment='微信openid'
    )
    # avatar = models.CharField(max_length=250, null=True, editable=False, verbose_name='微信头像', db_comment='微信头像')
    # nickname = models.CharField(
    #     max_length=100, null=True, editable=False, verbose_name="微信昵称", db_comment="微信昵称"
    # )

    phone = models.CharField(max_length=11, verbose_name='手机号码', db_comment='手机号码', unique=True)
    bank = models.CharField(max_length=100, verbose_name='银行', db_comment='银行', null=True, blank=True)
    bank_card_number = EncryptedCharField(verbose_name='银行卡号', db_comment='银行卡号', null=True, blank=True)
    card_number = EncryptedCharField(
        verbose_name='身份证号码', db_comment='身份证号码', null=True, blank=True
    )
    bank_operation_name = models.CharField(
        max_length=50, verbose_name='开户行名称', db_comment='开户行名称', null=True, blank=True
    )
    name = models.CharField(max_length=10, verbose_name='医生姓名', db_comment='医生姓名')
    gender = models.CharField(max_length=10, null=True, blank=True, verbose_name='性别', db_comment='性别')
    birthday = models.DateField(null=True, blank=True, verbose_name='出生日期', db_comment='出生日期')
    hospital = models.CharField(max_length=30, null=True, blank=True, verbose_name='医院', db_comment='医院')
    province = models.CharField(max_length=30, null=True, blank=True, verbose_name='省份', db_comment='省份')
    region = models.CharField(max_length=30, null=True, blank=True, verbose_name='大区', db_comment='大区')
    precinct = models.CharField(max_length=30, null=True, blank=True, verbose_name='片区', db_comment='片区')

    pic = models.URLField(max_length=250, verbose_name='行医执照', db_comment='行医执照', null=True, blank=True)
    sign_img = models.TextField(null=True, blank=True, verbose_name='签名图片', db_comment='签名图片')
    state = models.SmallIntegerField(verbose_name="认证状态", db_comment="认证状态", choices=STATE_CHOICES, default=0)
    cause = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='审核不通过的原因', db_comment='审核不通过的原因'
    )

    last_login = models.DateTimeField(
        editable=False, null=True, blank=True, verbose_name='最后登录时间', db_comment='最后登录时间'
    )
    is_subscribe = models.BooleanField(
        default=False, editable=False, verbose_name='关注公众号', db_comment='关注公众号'
    )

    def __str__(self):
        return f'{self.hospital}-{self.name}-{self.phone}'

    class Meta:
        ordering = ['-pk']
        verbose_name = '医生信息'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=['phone', "openid"], name='unique_doctor_phone_openid')
        ]

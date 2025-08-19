from django.db import models
import reversion
from utils.models import BaseModel


# Create your models here.


@reversion.register
class DiseasesCategory(BaseModel):
    title = models.CharField(max_length=30, verbose_name="分类名称", db_comment="分类名称")
    order = models.IntegerField(default=0, verbose_name="排序", db_comment="排序", help_text="倒叙")
    is_use = models.BooleanField(default=True, verbose_name="是否启用", db_comment="是否启用")

    class Meta:
        ordering = ["-order"]
        verbose_name = "疾病分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


@reversion.register
class QuestionBank(BaseModel):
    category = models.ForeignKey('DiseasesCategory', on_delete=models.CASCADE, verbose_name="分类", db_comment="分类")
    scope = models.CharField(max_length=30, verbose_name="调研范围", db_comment="调研范围")
    kind = models.CharField(
        verbose_name="题目类型", db_comment="题目类型", max_length=2,
        db_index=True,
        # 评分题=单选， 排序题=填空题
        choices=(("S", "单选题"), ("D", "多选题"), ("P", "评分题"), ("T", "排序题")),
    )
    title = models.CharField(max_length=100, verbose_name="题目名称", db_comment="题目名称")
    is_use = models.BooleanField(default=True, verbose_name="是否启用", db_comment="是否启用")

    class Meta:
        verbose_name = "题库"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


@reversion.register
class Option(BaseModel):
    question = models.ForeignKey(
        'survey.QuestionBank', on_delete=models.CASCADE, verbose_name="题目", db_comment="题目",
        related_name="options", null=True
    )
    title = models.CharField(max_length=100, verbose_name="选项名称", db_comment="选项名称")
    order = models.IntegerField(default=0, verbose_name="排序", db_comment="排序", help_text="倒叙")

    class Meta:
        ordering = ["-order"]
        verbose_name = "选项"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


@reversion.register
class CommitLog(BaseModel):
    category = models.ForeignKey(
        'DiseasesCategory', on_delete=models.CASCADE, verbose_name="分类", db_comment="分类", null=True
    )
    user = models.ForeignKey('user.Doctor', on_delete=models.CASCADE, verbose_name="用户", db_comment="用户")
    hospital = models.CharField(verbose_name="医院", db_comment="医院", max_length=100, null=True, blank=True)
    phone = models.CharField(verbose_name="手机号", db_comment="手机号", max_length=11, null=True, blank=True)
    level = models.ForeignKey(
        "agreement.LaborFeeLevel", on_delete=models.CASCADE, verbose_name='劳务费档位', db_comment='劳务费档位',
        null=True, blank=True
    )
    state = models.ForeignKey(
        "works.WorksState", on_delete=models.CASCADE, verbose_name='状态', db_comment='状态', null=True, blank=True
    )
    payment_time = models.DateTimeField(verbose_name="支付时间", db_comment="支付时间", null=True, blank=True)
    payment_amount = models.DecimalField(
        verbose_name="支付金额", db_comment="支付金额", default=0.00, max_digits=10, decimal_places=2
    )

    data = models.JSONField(verbose_name="提交数据", db_comment="提交的答题数据", editable=False)

    class Meta:
        verbose_name = "提交记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '调研提交记录'

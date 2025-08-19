from utils.models import BaseModel
from agreement.models import Doctor, LaborFeeLevel
from DjangoUeditor.models import UEditorField
from qiniuupload.fields import QiniuField
from django.db import models
import reversion


@reversion.register
class WorksCategory(BaseModel):
    title = models.CharField(max_length=30, verbose_name="分类名称", db_comment="分类名称")
    order = models.IntegerField(default=0, verbose_name="排序", db_comment="排序", help_text="倒叙")

    class Meta:
        ordering = ["-order"]
        verbose_name = "分类管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


@reversion.register
class WorksState(BaseModel):
    title = models.CharField(max_length=30, verbose_name="状态名称", db_comment="状态名称")
    order = models.IntegerField(default=0, verbose_name="排序", db_comment="排序", help_text="倒叙")

    class Meta:
        ordering = ["-order"]
        verbose_name = "状态管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


@reversion.register
class Works(BaseModel):
    title = models.CharField(max_length=200, verbose_name='标题', db_comment='标题')
    author = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='作者', db_comment='作者')
    hospital = models.CharField(verbose_name="医院", db_comment="医院", max_length=100, null=True, blank=True, editable=False)
    phone = models.CharField(verbose_name="手机号", db_comment="手机号", max_length=11, null=True, blank=True)
    category = models.ForeignKey(
        WorksCategory, on_delete=models.CASCADE, verbose_name='素材类型', db_comment='素材类型'
    )
    level = models.ForeignKey(
        LaborFeeLevel, on_delete=models.CASCADE, verbose_name='劳务费档位', db_comment='劳务费档位'
    )
    state = models.ForeignKey(WorksState, on_delete=models.CASCADE, verbose_name='状态', db_comment='状态')
    video_upload = QiniuField(max_length=512, null=True, blank=True, verbose_name='文件上传', db_comment='文件上传')
    payment_time = models.DateTimeField(verbose_name="支付时间", db_comment="支付时间", null=True, blank=True)
    payment_amount = models.DecimalField(
        verbose_name="支付金额", db_comment="支付金额", default=0.00, max_digits=10, decimal_places=2
    )
    is_push = models.BooleanField(default=False, verbose_name='是否已推送', db_comment='是否已推送')
    sale_name = models.CharField(verbose_name="销售姓名", db_comment="销售姓名", max_length=50, null=True, blank=True)

    content = UEditorField(null=True, blank=True, verbose_name='内容', db_comment='内容')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pk']
        verbose_name = '作品管理'
        verbose_name_plural = verbose_name


@reversion.register
class CaseWorksState(BaseModel):
    title = models.CharField(max_length=30, verbose_name="状态名称", db_comment="状态名称")
    order = models.IntegerField(default=0, verbose_name="排序", db_comment="排序", help_text="倒叙")

    class Meta:
        ordering = ["-order"]
        # verbose_name = "病例状态管理"
        verbose_name = "疾病认知状态管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


@reversion.register
class Case(BaseModel):
    title = models.CharField(max_length=30, verbose_name='标题', db_comment='标题', null=True, blank=True)
    author = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, verbose_name='作者', db_comment='作者', null=True, blank=True
    )
    hospital = models.CharField(verbose_name="医院", db_comment="医院", max_length=100, null=True, blank=True)
    phone = models.CharField(verbose_name="手机号", db_comment="手机号", max_length=11, null=True, blank=True)
    category = models.CharField(
        verbose_name='素材类型', db_comment='素材类型', editable=False, max_length=12, default="SLE/LN",
        choices=(
            ("SLE/LN", "SLE/LN"),
            ("MG", "MG"),
        )
    )
    level = models.ForeignKey(
        LaborFeeLevel, on_delete=models.CASCADE, verbose_name='劳务费档位', db_comment='劳务费档位', null=True,
        blank=True
    )
    state = models.ForeignKey(
        CaseWorksState, on_delete=models.CASCADE, verbose_name='状态', db_comment='状态', null=True, blank=True
    )
    # video_upload = QiniuField(max_length=512, null=True, blank=True, verbose_name='文件上传', db_comment='文件上传')
    payment_time = models.DateTimeField(verbose_name="支付时间", db_comment="支付时间", null=True, blank=True)
    payment_amount = models.DecimalField(
        verbose_name="支付金额", db_comment="支付金额", default=0.00, max_digits=10, decimal_places=2
    )
    is_push = models.BooleanField(default=False, verbose_name='是否已推送', db_comment='是否已推送')
    sale_name = models.CharField(verbose_name="销售姓名", db_comment="销售姓名", max_length=50, null=True, blank=True)

    # 病例收集 表单
    sex = models.SmallIntegerField(choices=((0, '男'), (1, '女'),), verbose_name='性别', db_comment='性别')
    age = models.SmallIntegerField(verbose_name='年龄', db_comment='年龄')
    case_now = models.CharField(max_length=350, verbose_name='现病史', db_comment='现病史')
    sle = models.CharField(max_length=350, verbose_name='SLE病变部位', db_comment='SLE病变部位')
    case_time = models.DateTimeField(verbose_name='发病时间', db_comment='发病时间')
    history_scheme = models.CharField(max_length=350, verbose_name='既往治疗方案', db_comment='既往治疗方案')
    now_scheme = models.CharField(max_length=350, verbose_name='现今治疗方案', db_comment='现今治疗方案')
    metrics = models.CharField(max_length=1200, verbose_name='关键检测指标', db_comment='关键检测指标')

    class Meta:
        ordering = ['-pk']
        # verbose_name = '病例征集'
        verbose_name = '疾病认知调研'
        verbose_name_plural = verbose_name

    def __str__(self):
        # return '病例征集'
        return '疾病认知调研'


@reversion.register
class MedCase(BaseModel):
    disease = models.ForeignKey("Disease", on_delete=models.CASCADE, verbose_name='疾病', db_comment='疾病', null=True,
                                blank=True, related_name="dis_med_cases")
    author = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, verbose_name='作者', db_comment='作者', null=True, blank=True,
        related_name="doctor_med_cases"
    )
    level = models.ForeignKey(
        LaborFeeLevel, on_delete=models.CASCADE, verbose_name='劳务费档位', db_comment='劳务费档位', null=True,
        blank=True
    )
    state = models.ForeignKey(
        CaseWorksState, on_delete=models.CASCADE, verbose_name='状态', db_comment='状态', null=True, blank=True
    )
    # video_upload = QiniuField(max_length=512, null=True, blank=True, verbose_name='文件上传', db_comment='文件上传')
    payment_time = models.DateTimeField(verbose_name="支付时间", db_comment="支付时间", null=True, blank=True)
    payment_amount = models.DecimalField(
        verbose_name="支付金额", db_comment="支付金额", default=0.00, max_digits=10, decimal_places=2
    )
    is_push = models.BooleanField(default=False, verbose_name='是否已推送', db_comment='是否已推送')

    # 病例收集 表单
    # data = models.JSONField(verbose_name="表单病例收集", db_comment="表单病例收集", editable=False)
    data = models.JSONField(verbose_name="表单疾病认知收集", db_comment="表单疾病认知收集", editable=False)

    class Meta:
        ordering = ['-pk']
        # verbose_name = '新病例征集'
        verbose_name = '新疾病认知征集'
        verbose_name_plural = verbose_name


@reversion.register
class Disease(BaseModel):
    title = models.CharField(max_length=100, verbose_name="疾病名称", db_comment="疾病名称")
    # desc = models.CharField(max_length=255, verbose_name="备注", help_text="疾病认知提交顶部备注", db_comment="备注",
    desc = models.CharField(max_length=255, verbose_name="备注", help_text="疾病认知提交顶部备注", db_comment="备注",
                            null=True, blank=True)
    body = UEditorField(verbose_name='介绍', db_comment='介绍')
    questions = models.ManyToManyField("Question", verbose_name="题目", related_name="question_diseases", blank=True)
    is_use = models.BooleanField(default=True, verbose_name="是否启用", db_comment="是否启用")
    order = models.IntegerField(default=0, verbose_name="排序", db_comment="排序", help_text="倒序")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "疾病管理"
        verbose_name_plural = verbose_name
        ordering = ['-order', '-id']


class QuestionKindChoices(models.IntegerChoices):
    sf = 1, "短填空"
    lf = 2, "长填空"
    sc = 3, "单选"
    mc = 4, "多选"
    date = 5, "日期"
    ui = 6, "上传图片"


@reversion.register
class Question(BaseModel):
    kind = models.PositiveSmallIntegerField(verbose_name="题目类型", db_comment="题目类型", db_index=True,
                                            choices=QuestionKindChoices.choices, default=QuestionKindChoices.sf
                                            )
    title = models.CharField(max_length=100, verbose_name="题目名称", db_comment="题目名称")
    desc = models.CharField(max_length=100, verbose_name="单位/备注", db_comment="单位/备注", null=True, blank=True)
    is_use = models.BooleanField(default=True, verbose_name="是否启用", db_comment="是否启用")
    required = models.BooleanField(default=True, verbose_name="是否必填", db_comment="是否必填")
    order = models.IntegerField(default=0, verbose_name="排序", db_comment="排序", help_text="正序")

    class Meta:
        verbose_name = "题库"
        verbose_name_plural = verbose_name
        ordering = ['order', '-id']

    def __str__(self):
        return self.title


@reversion.register
class Item(BaseModel):
    question = models.ForeignKey(
        'works.Question', on_delete=models.CASCADE, verbose_name="题目", db_comment="题目",
        related_name="items", null=True
    )
    title = models.CharField(max_length=100, verbose_name="选项名称", db_comment="选项名称")
    order = models.IntegerField(default=0, verbose_name="排序", db_comment="排序", help_text="倒序")

    class Meta:
        ordering = ['-order', '-id']
        verbose_name = "选项"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

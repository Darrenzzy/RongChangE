import logging
import typing

from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from survey.models import DiseasesCategory, QuestionBank, Option, CommitLog
from survey.serializers import ListDiseasesCategorySerializer, CreateQuestionBankSerializer, \
    ListMyHistoryViewSetSerializer, CreateCommitLogSerializer
from utils.base import RegisterDoctorAuthentication
from utils.throttle_cache_tools import check_throttle_limit_range
from utils.tools import convert_array_to_dictionary
from utils.ym_restframework.pagination import YmPageNumberPagination
from vendor.abnormal.fmt_log_exception import fmt_error
from works.models import WorksState

log_except = logging.getLogger("except")


# Create your views here.
class DiseasesCategoryViewSet(
    GenericViewSet,
    mixins.ListModelMixin
):
    authentication_classes = [RegisterDoctorAuthentication]
    serializer_class = ListDiseasesCategorySerializer
    queryset = DiseasesCategory.objects.filter(is_use=True)


class QuestionBankViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    lookup_field = 'category_id'
    authentication_classes = [RegisterDoctorAuthentication]
    queryset = QuestionBank.objects.filter(category__is_use=True, is_use=True)
    serializer_class = CreateQuestionBankSerializer
    throttle_classes = []

    def retrieve(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        # 速率限制，params：
        # 当前一分钟内最多请求5次该接口
        is_wait, wait_throttle = check_throttle_limit_range(
            throttle_key=[f"throttle:api:survey:question_retrieve:{request.user.pk}:{self.kwargs[lookup_url_kwarg]}"],
            throttle_top=[3],
            timeout=[60]
        )
        if is_wait:
            return Response({"code": 400, "msg": "访问太过频繁了哦，请稍后再试", "data": []})

        try:
            queryset = self.queryset.filter(**filter_kwargs)
        except ValueError:
            return Response({"code": 400, "msg": "参数异常", "data": []})

        if not queryset.exists():
            return Response({"code": 400, "msg": "题库不足，请联系管理员完善题库", "data": []})

        # 获取所有题目，不再限制数量
        questions = queryset.values("id", "scope", "kind", "title").order_by('id')
        
        if questions:
            question_ids = [q['id'] for q in questions]
            options = (Option.objects.filter(question_id__in=question_ids).order_by("-order", "pk")
                       .values("id", "question_id", "title"))
            option_map = convert_array_to_dictionary(array=options, target_key_name='question_id', drop_target_key=True)
            return Response({
                "code": 200, "msg": "success",
                "data": [{**q, "options": option_map.get(q['id'], [])} for q in questions]
            })

        return Response({"code": 400, "msg": "题库不足，请联系管理员完善题库", "data": []})

    def create(self, request, *args, **kwargs):
        _category = request.data.get('category', None)
        if not _category:
            return Response({"code": 400, "msg": "参数异常", "data": []})
        try:
            _category = int(_category)
        except ValueError:
            return Response({"code": 400, "msg": "参数异常", "data": []})

        # 速率限制，params：
        # 当前x分钟内最多请求x次该接口
        is_wait, wait_throttle = check_throttle_limit_range(
            throttle_key=[
                f"throttle:api:survey:question_create:{_category}:{request.user.pk}",
                f"throttle:api:survey:question_create_10:{_category}:{request.user.pk}"
            ],
            throttle_top=[1, 5],
            timeout=[1, 60]
        )
        if is_wait:
            return Response({"code": 400, "msg": "访问太过频繁了哦，请稍后再试", "data": []})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attrs = serializer.validated_data

        category = attrs.get("category")
        data = attrs.get("data")
        try:
            target: typing.List[typing.Dict[str, typing.Any]] = [
                {
                    "id": int(d['id']),
                    "title": d['title'],
                    "scope": d['scope'],
                    "kind": d['kind'],
                    "options": [
                        {
                            "id": int(o['id']),
                            "title": o['title']
                        }
                        for o in d['options']
                    ]
                }
                for d in data
            ]
        except (KeyError, ValueError):
            return Response({"code": 400, "msg": "提交参数异常", "data": []})

        # 校验题目
        question_ids, option_ids = [], []
        [
            (
                question_ids.append(x['id']),
                option_ids.extend([y['id'] for y in x['options'] if y['id']])
            )
            for x in target
        ]

        question_map = {
            x['id']: {'title': x['title'], 'kind': x['kind'], 'scope': x['scope']}
            for x in QuestionBank.objects.filter(id__in=question_ids, category_id=category.pk, is_use=True).
            values("id", "title", "kind", "scope")
        }
        option_base = Option.objects.filter(id__in=option_ids).values("id", "title", "question_id")

        # 题目下的选项
        quest_option_map = {}
        for _o in option_base:
            if _o['question_id'] in quest_option_map:
                quest_option_map[_o['question_id']].append({"id": _o['id'], "title": _o['title']})
            else:
                quest_option_map[_o['question_id']] = [{"id": _o['id'], "title": _o['title']}]

        option_map = {
            x['id']: {"question_id": x['question_id'], "title": x['title']} for x in option_base
        }

        for _t in target:
            _question = question_map.get(_t['id'])
            if not _question:
                return Response({"code": 400, "msg": "题目不存在", "data": []})

            _t['title'] = _question['title']
            _t['kind'] = _question['kind']
            _t['scope'] = _question['scope']

            # 评分题=单选， 排序题=填空题
            # choices = (("S", "单选题"), ("D", "多选题"), ("P", "评分题"), ("T", "排序题")),
            # 题目类型校验
            this_options_lens = len(_t['options'])
            match _t['kind']:
                case 'S':
                    if this_options_lens != 1:
                        return Response({"code": 400, "msg": "单选题只能有一个选项", "data": []})
                case 'D':
                    if this_options_lens < 1:
                        return Response({"code": 400, "msg": "多选题至少需要一个选项", "data": []})
                case 'P':
                    if this_options_lens != 1:
                        return Response({"code": 400, "msg": "评分题只能有一个选项", "data": []})
                case 'T':
                    if this_options_lens != 1:
                        return Response({"code": 400, "msg": "排序题只能回复一个选项内容", "data": []})
                    if _t['options'][0].get("id") != 0:
                        return Response({"code": 400, "msg": "排序题的选项id必须为0", "data": []})
                case _:
                    return Response({"code": 400, "msg": "题目类型错误", "data": []})

            # 获取当前题目下的所有选项列表
            current_options = {oo['id']: oo['title'] for oo in quest_option_map.get(_t['id'], [])}
            if _t['kind'] != 'T':  # 排序题=填空题
                for y in _t['options']:
                    # 先判断提交的选项是否属于当前题目
                    if not current_options.get(y['id']):
                        return Response({"code": 400, "msg": "选项不存在", "data": []})

                    _option = option_map.get(y['id'])
                    if not _option:
                        return Response({"code": 400, "msg": "选项不存在", "data": []})

                    y['title'] = _option['title']
                    y['question_id'] = _option['question_id']
                    if _option['question_id'] != _t['id']:
                        return Response({"code": 400, "msg": "选项不属于题目", "data": []})

        try:
            current_user = request.user
            CommitLog.objects.create(
                category_id=category.pk,
                user_id=current_user.pk,
                hospital=current_user.hospital,
                phone=current_user.phone,
                data=target,
            )
        except Exception as e:
            fmt_error(
                log_except, title=f"调研问卷提交失败", e=e,
                other={"attrs": attrs, "target": target, "category": category.pk},
                tag=["调研问卷提交", '调研问卷提交失败'],
                request=request
            )
            return Response({"code": 400, "msg": "提交失败", "data": []})
        return Response({"code": 200, "msg": "success", "data": []})


class MyHistoryViewSet(GenericViewSet, mixins.ListModelMixin):
    """
    我的调研问卷
    """

    queryset = CommitLog.objects.all()
    authentication_classes = [RegisterDoctorAuthentication]
    serializer_class = ListMyHistoryViewSetSerializer
    pagination_class = YmPageNumberPagination

    def get_queryset(self):
        base = CommitLog.objects.filter(
            user_id=self.request.user.pk, category__is_use=True
        ).order_by("-pk")

        # to_do 待审核任务：读取后台状态：空
        # done 已审核：读取后台状态：已支付
        state = self.request.query_params.get("state")
        if state == "to_do":
            return base.filter(state_id__isnull=True)
        elif state == "done":
            done_cate = WorksState.objects.filter(title="已支付").first()
            return base.filter(state_id=done_cate.pk) if done_cate else base.none()
        else:
            return base.none()


class QuestionnaireDetailViewSet(GenericViewSet):
    """
    问卷详情接口 - 获取指定问卷分类下的所有问题
    """
    authentication_classes = [RegisterDoctorAuthentication]
    
    def retrieve(self, request, *args, **kwargs):
        """
        获取指定问卷分类下的所有问题和选项
        
        URL: GET /api/survey/questionnaire-detail/{category_id}/
        """
        category_id = kwargs.get('pk')
        
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return Response({
                "code": 400,
                "msg": "问卷分类ID格式错误",
                "data": []
            })
        
        # 验证问卷分类是否存在且启用
        category = DiseasesCategory.objects.filter(id=category_id, is_use=True).first()
        if not category:
            return Response({
                "code": 400,
                "msg": "问卷分类不存在或未启用",
                "data": []
            })
        
        # 获取该分类下所有启用的问题
        questions = QuestionBank.objects.filter(
            category_id=category_id,
            is_use=True
        ).values("id", "scope", "kind", "title").order_by('id')
        
        if not questions:
            return Response({
                "code": 400,
                "msg": "该问卷暂无题目",
                "data": []
            })
        
        # 获取所有问题的选项
        question_ids = [q['id'] for q in questions]
        options = Option.objects.filter(
            question_id__in=question_ids
        ).values("id", "question_id", "title", "order").order_by("question_id", "-order", "pk")
        
        # 将选项按问题ID分组
        from utils.tools import convert_array_to_dictionary
        option_map = convert_array_to_dictionary(
            array=options, 
            target_key_name='question_id', 
            drop_target_key=True
        )
        
        # 组装响应数据
        questionnaire_data = {
            "category": {
                "id": category.id,
                "title": category.title
            },
            "questions": [
                {
                    **q,
                    "options": option_map.get(q['id'], [])
                }
                for q in questions
            ]
        }
        
        return Response({
            "code": 200,
            "msg": "success",
            "data": questionnaire_data
        })


class CommitLogCreateViewSet(GenericViewSet, mixins.CreateModelMixin):
    """
    外部API提交调研记录
    用于第三方系统直接向survey_commitlog表提交数据
    """
    serializer_class = CreateCommitLogSerializer
    queryset = CommitLog.objects.all()
    authentication_classes = []  # 移除认证要求
    permission_classes = []      # 移除权限要求
    
    def create(self, request, *args, **kwargs):
        """
        提交调研记录数据到survey_commitlog表
        
        请求示例:
        POST /api/survey/external/commitlog/
        {
            "category_id": 1,
            "user_id": 1,
            "hospital": "北京协和医院",
            "phone": "13800138000",
            "level_id": 1,
            "state_id": 1,
            "payment_time": "2024-08-20T10:00:00Z",
            "payment_amount": 100.50,
            "data": [
                {
                    "id": 1,
                    "title": "题目标题",
                    "scope": "调研范围",
                    "kind": "S",
                    "options": [
                        {
                            "id": 1,
                            "title": "选项标题"
                        }
                    ]
                }
            ]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            commit_log = serializer.save()
            return Response({
                "code": 200,
                "msg": "提交成功",
                "data": {
                    "id": commit_log.id,
                    "created_at": commit_log.created_at
                }
            }, status=201)
        except Exception as e:
            fmt_error(
                log_except, 
                title="外部API提交调研记录失败", 
                e=e,
                other={"request_data": request.data},
                tag=["外部API", "调研记录提交失败"],
                request=request
            )
            return Response({
                "code": 400,
                "msg": f"提交失败: {str(e)}",
                "data": []
            }, status=400)

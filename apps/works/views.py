from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.base import RegisterDoctorAuthentication
from utils.ym_restframework.decorators import ym_api
from utils.ym_restframework.pagination import YmPageNumberPagination
from works.models import Case, CaseWorksState, MedCase, Disease
from works.serializers import CreateCaseSerializer, ListCaseSerializer, DiseaseSerializer, DiseaseRetrieveSerializer, \
    MedCaseSerializer, CaseAndMedCaseSerializer
from works.throttles import MedCaseUserRateThrottle


class CaseViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    authentication_classes = [RegisterDoctorAuthentication]
    serializer_class = CreateCaseSerializer
    queryset = Case.objects.all()
    pagination_class = YmPageNumberPagination

    def get_serializer_class(self):
        return {"create": CreateCaseSerializer, "list": CaseAndMedCaseSerializer}.get(self.action, CreateCaseSerializer)

    # def get_queryset(self):
    #     # to_do 待审核任务：读取后台状态：空
    #     # done 已审核：读取后台状态：已支付
    #     state = self.request.query_params.get("state")
    #     base = self.queryset.filter(author_id=self.request.user.pk)
    #     if state == "to_do":
    #         return base.filter(state_id__isnull=True)
    #     elif state == "done":
    #         done_cate = CaseWorksState.objects.filter(title="已支付").first()
    #         return base.filter(state_id=done_cate.pk) if done_cate else base.none()
    #     else:
    #         return base.none()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # to_do 待审核任务：读取后台状态：空
        # done 已审核：读取后台状态：已支付
        state = self.request.query_params.get("state")
        # 获取老病例收集
        case_queryset = queryset.filter(author_id=self.request.user.pk)
        # 获取新病例收集
        med_case_queryset = MedCase.objects.filter(author_id=self.request.user.pk)

        if state == "to_do":
            case_queryset = case_queryset.filter(state_id__isnull=True)
            med_case_queryset = med_case_queryset.filter(state_id__isnull=True)
        elif state == "done":
            done_cate = CaseWorksState.objects.filter(title="已支付").first()
            case_queryset = case_queryset.filter(state_id=done_cate.pk) if done_cate else case_queryset.none()
            med_case_queryset = med_case_queryset.filter(
                state_id=done_cate.pk) if done_cate else med_case_queryset.none()
        else:
            case_queryset = case_queryset.none()
            med_case_queryset = med_case_queryset.none()

            # 合并数据集
        from itertools import chain
        queryset = [item for item in
                    chain(case_queryset, med_case_queryset)]
        # 按照时间倒序排序
        queryset.sort(key=lambda item: item.created_at.timetuple(), reverse=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@ym_api
class DiseaseView(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = (RegisterDoctorAuthentication,)
    queryset = Disease.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('is_use',)

    ym_serializer_classes = {
        "list": DiseaseSerializer,
        "retrieve": DiseaseRetrieveSerializer
    }


@ym_api
class MedCaseView(GenericViewSet, mixins.CreateModelMixin):
    authentication_classes = (RegisterDoctorAuthentication,)
    serializer_class = MedCaseSerializer
    throttle_classes = (MedCaseUserRateThrottle,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(None, status=status.HTTP_201_CREATED, headers=headers)

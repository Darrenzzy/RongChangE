from user.models import Doctor
from user.serializers import (
    DoctorRetrieveSerializer,
    DoctorCreateSerializer,
    DoctorProfileUpdateSerializer
)
from utils.sms import SMS
from qiniuupload import qiniuupload
from rest_framework import status, mixins
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django.core.cache import cache
from django.http import Http404

from utils.ym_restframework.exceptions import TextValidationError
from vendor.wechat.official_account import WeChatUserInfo
from utils.base import EventEnum, HZKPOpenidAuthentication
import logging

logger = logging.getLogger('default')
wechat_logger = logging.getLogger('wechat')


class VerificationCodeView(APIView):
    """ 发送验证码 """

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if not phone:
            return Response({'status': 1, 'msg': '手机号不能为空'}, status=status.HTTP_200_OK)

        if not Doctor.objects.filter(phone=phone).exists():
            return Response({'status': 1, 'msg': '您不是白名单用户'}, status=status.HTTP_200_OK)

        if cache.get(f'code:{phone}:latestSend'):
            return Response({'status': 1, 'msg': '验证码发送太频繁'}, status=status.HTTP_200_OK)

        is_success = SMS.send(phone)
        return Response({'status': 0, 'msg': '短信验证码已发送' if is_success else "短信服务异常,请联系管理员~"},
                        status=status.HTTP_200_OK)


class QiniuCloudTokenView(APIView):
    """ 七牛云上传凭证 """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        key = request.query_params.get('key')
        if not key:
            return Response({'msg': '缺少key参数'}, status=status.HTTP_400_BAD_REQUEST)
        token = qiniuupload.get_token(key=key)
        return Response({'token': token})


class DoctorViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin
):
    """ 医生信息 """

    queryset = Doctor.objects.all()
    serializer_class = DoctorRetrieveSerializer
    lookup_field = 'openid'

    def get_authentication_classes(self):
        if self.action == 'retrieve':
            return [HZKPOpenidAuthentication()]
        return []

    def get_serializer_class(self):
        serializer_mapping = {
            'retrieve': DoctorRetrieveSerializer,
            'create': DoctorCreateSerializer,  # 回到原来的序列化器
        }
        return serializer_mapping[self.action]

    def create(self, request, *args, **kwargs):
        # 先使用原来的序列化器验证基础字段
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attrs = serializer.validated_data
        
        # 验证openid是否已被使用
        openid_history = Doctor.objects.filter(openid=attrs["openid"], state__in=[1, 2]).exists()
        if openid_history:
            raise TextValidationError(detail="您当前微信为已使用状态，请勿重复注册，谢谢", code=200)

        # 查找现有医生记录
        doctor = Doctor.objects.filter(phone=attrs["phone"]).first()
        if not doctor:
            raise TextValidationError(detail="您当前非邀请用户，请联系您的专员开通访问权限", code=200)
        
        # 检查当前状态
        if doctor.state == 1:
            raise TextValidationError(detail="恭喜您注册成功，请耐心等待，审核时间为1-3天。", code=200)
        if doctor.state in [1, 2]:
            raise TextValidationError(detail=f"用户{doctor.get_state_display()}", code=200)
        
        # 验证并设置openid
        if doctor.openid != attrs['openid']:
            if Doctor.objects.filter(openid=attrs['openid']).exists():
                raise TextValidationError(detail="您当前微信OPENID为已使用状态，请勿重复注册，谢谢", code=200)
            doctor.openid = attrs['openid']
        
        # 设置状态为待审核
        doctor.state = 1
        doctor.pic = attrs['pic']
        
        # 从request.data中获取额外的字段并更新
        extra_fields = request.data
        field_mapping = {
            'name': 'name',
            'gender': 'gender', 
            'birthday': 'birthday',
            'card_number': 'card_number',
            'bank': 'bank',
            'bank_card_number': 'bank_card_number',
            'bank_operation_name': 'bank_operation_name',
            'hospital': 'hospital',
            'province': 'province',
            'region': 'region',
            'precinct': 'precinct',
            'sign_img': 'sign_img'
        }
        
        for field_name, model_field in field_mapping.items():
            if field_name in extra_fields and extra_fields[field_name] is not None:
                setattr(doctor, model_field, extra_fields[field_name])
        
        # 保存所有更新
        doctor.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            "code": 200,
            "msg": "资料提交成功，请耐心等待审核", 
            "data": {}
        }, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response({}, status=status.HTTP_200_OK)


class UserSubscrebeView(APIView):
    authentication_classes = [HZKPOpenidAuthentication]

    # permission_classes = []

    def get(self, request, *args, **kwargs):
        user, openid = request.user, request.auth
        if openid:
            is_subscribe = WeChatUserInfo.get_user_subscribe_status(openid)
            if user and user.is_subscribe != is_subscribe:
                user.is_subscribe = is_subscribe
                user.save(update_fields=['is_subscribe'])
            return Response({'is_subscribe': is_subscribe})
        return Response({'is_subscribe': False})


class UserStatusView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        phone = request.query_params.get('phone')
        if not phone:
            return Response({'status': 1, 'msg': '手机号不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            doctor = Doctor.objects.get(phone=phone)
            
            # 检查是否提交了除手机号和姓名之外的其他信息
            has_additional_info = any([
                doctor.bank,
                doctor.bank_card_number,
                doctor.card_number,
                doctor.bank_operation_name,
                doctor.hospital,
                doctor.province,
                doctor.region,
                doctor.precinct
                # doctor.pic
            ]) 
           
            if doctor.state == 2:
                status_code = 2
                status_msg = "已认证"
            elif doctor.state == 3:
                status_code = 3
                status_msg = "不通过"
            elif has_additional_info or doctor.state == 1:
                status_code = 1
                status_msg = "已提交资料，待审核"
            else:
                status_code = 0
                status_msg = "初始化"
            
            return Response({
                'status': 0,
                'data': {
                    'user_status': status_code,
                    'status_msg': status_msg
                }
            }, status=status.HTTP_200_OK)
            
        except Doctor.DoesNotExist:
            return Response({
                'status': 0,
                'data': {
                    'user_status': -1,
                    'status_msg': "未注册"
                }
            }, status=status.HTTP_200_OK)


class WechatCallbackView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """
        微信回调事件通知
        @params openid:访问用户openid
        @params event key: 事件REY值，grscene 为前缀，后面为二维码的参数值
        @params event msg type:
            image:图片
            text: 文字
            event:事件
            voice: 语音
            video:视频
            shortvideo:小视频
            location:地理位置
            link:链接
        @params event:
            subscribe:关注
            unsubscribe: 取消关注
            CLICK:点击菜单
            SCAN:扫描二维码
            VIEW:跳转
            LOCATION:地理位置
        """

        post_data = request.POST.copy()
        event = post_data.get('event')
        openid = post_data.get('openid')
        wechat_logger.info(f'公众号回调消息 => openid={openid}, event={event}')

        if event == EventEnum.SUBSCRIBE:
            # 关注
            rows = Doctor.objects.filter(openid=openid).update(is_subscribe=True)
            if rows:
                wechat_logger.info(f'公众号回调消息 => {openid}关注了公众号')
        if event == EventEnum.UNSUBSCRIBE:
            # 取关
            rows = Doctor.objects.filter(openid=openid).update(is_subscribe=False)
            if rows:
                wechat_logger.info(f'公众号回调消息 => {openid}取关了公众号')
        return Response(status=status.HTTP_200_OK)

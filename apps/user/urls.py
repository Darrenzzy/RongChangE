from django.urls import path
from rest_framework.routers import SimpleRouter
from user.views import (
    VerificationCodeView,
    QiniuCloudTokenView,
    DoctorViewSet,
    UserSubscrebeView,
    WechatCallbackView,
)

router = SimpleRouter()
# 获取医生信息
router.register('doctor', DoctorViewSet, basename='doctor')

urlpatterns = [
    # 发送短信验证码
    path(r'code/', VerificationCodeView.as_view(), name='verification_code'),
    # 获取七牛云上传凭证
    path(r'qiniuToken/', QiniuCloudTokenView.as_view(), name='qiniu_token'),
    # 查询用户是否已关注公众号
    path(r'subscribe/', UserSubscrebeView.as_view(), name='subscribe'),
    path(r'wechatCallback/', WechatCallbackView.as_view(), name='wechat_callback'),
]

urlpatterns += router.urls

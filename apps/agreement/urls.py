from agreement.views import (
    PrivacyPolicyView, 
)
from django.urls import path
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

urlpatterns = [
    # 获取隐私条款
    path(r'privacyPolicy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
]

urlpatterns += router.urls

from agreement.models import PrivacyPolicy
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response


class PrivacyPolicyView(APIView):
    """ 隐私条款 """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        policy_content = cache.get('agreement:privacyPolicy:active')
        if not policy_content:
            policy = PrivacyPolicy.objects.filter(state=PrivacyPolicy.ACTIVE).only('content').first()
            if policy:
                policy_content = policy.content
                cache.set('agreement:privacyPolicy:active', policy_content, timeout=None)
        return Response({'content': policy_content})

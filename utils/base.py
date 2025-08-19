from datetime import datetime

from user.models import Doctor
from django.core.exceptions import ValidationError
from django.utils.deprecation import MiddlewareMixin
from rest_framework import serializers, authentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from typing import Optional
from enum import Enum
import re
import logging

from utils.ym_restframework.exceptions import TextValidationError

logger = logging.getLogger('api')


class ApiLoggingMiddleware(MiddlewareMixin):

    def __call__(self, request):
        if request.path.startswith('/api/'):
            logger.info(
                f'path={request.path}, method={request.method}, params={request.GET}, payload={request.body}, headers={request.headers}')
        return super().__call__(request)


class HZKPPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    max_page_size = 50


class IsUserOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.creator and request.user.id == obj.creator_id


class HZKPOpenidAuthentication(authentication.BaseAuthentication):
    AUTHENTICATION_FIELD = 'HTTP_OPENID'

    def authenticate(self, request):
        openid = request.META.get(self.AUTHENTICATION_FIELD)
        user = Doctor.objects.filter(openid=openid).first()
        if not user or not user.last_login:
            return None, openid
        user.last_login = datetime.now()
        user.save(update_fields=['last_login'])
        return user, user.openid


class RegisterDoctorAuthentication(authentication.BaseAuthentication):
    AUTHENTICATION_FIELD = 'HTTP_OPENID'

    def authenticate(self, request):
        openid = request.META.get(self.AUTHENTICATION_FIELD)
        user = Doctor.objects.filter(openid=openid, state=2).first()
        if not user:
            raise TextValidationError('请先完成认证哦')

        user.last_login = datetime.now()
        user.save(update_fields=['last_login'])
        user.is_authenticated = True
        return user, user.openid


class PhoneValidator:
    regex = r'^1[3-9]\d{9}'
    code = 'invalid'
    message = '手机号不合法'

    def __call__(self, value) -> Optional[ValidationError]:
        match = re.search(self.regex, value)
        if not match:
            raise ValidationError(self.message, code=self.code, params={'value': value})


class EventEnum(str, Enum):
    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'
    CLICK = 'click'
    SCAN = 'scan'
    VIEW = 'view'
    LOCATION = 'location'

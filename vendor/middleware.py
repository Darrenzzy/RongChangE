#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import threading
import uuid

from django.http import HttpResponseForbidden, HttpRequest
from django.utils.deprecation import MiddlewareMixin

from vendor.web_authentication.signature import SignatureHelper

logger, log_signature = logging.getLogger("request"), logging.getLogger("signature")

ignore_path = {
    '/',
}


def get_ip_address(request):
    try:
        ip_addr = request.META.get("HTTP_X_ORIGINAL_FORWARDED_FOR")
        if not ip_addr:
            ip_addr = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', '')
    except Exception as e:
        ip_addr = request.get('REMOTE_ADDR', '')
    return ip_addr


class CsrfCloseMiddleware(MiddlewareMixin):
    """ 关闭csrf """

    def process_request(self, request):
        request.csrf_processing_done = True


API_PREFIX_NAME = '/api'


class RequestLogPrintMiddleware(MiddlewareMixin):
    """ 请求日志打印 """

    def process_request(self, request):

        path = request.path
        if not path or not path.startswith(API_PREFIX_NAME) or path in ignore_path:
            return

        request_id = request.META.get("HTTP_X_REQUEST_ID")
        if request_id is None:
            request_id = str(uuid.uuid4())

        request.x_request_id = str(request_id)
        request._proxy_server_ip_address = get_ip_address(request)
        try:
            body = json.loads(request.body)
        except Exception:
            body = request.POST

        log_msg = {
            "transform": "request",
            'path': path,
            'request_id': request_id,
            'method': request.method,
            'scheme': request.scheme,
            'headers': f"{dict(request.META)}",
            'cookies': f"{dict(request.COOKIES)}",
            'content_type': request.content_type,
            'params': request.GET or None,
            'body': body or None
        }
        if request.FILES:
            log_msg['files'] = {
                key: [
                    {
                        'name': file_obj.name,
                        'size': f'{str(round(file_obj.size / 1024, 2))} KB'
                    } for file_obj in request.FILES.getlist(key)
                ]
                for key in request.FILES
            }

        try:
            logger.info(json.dumps({"msg": log_msg, "tag": ["api-middleware", "process_request"]}, ensure_ascii=False))
        except:
            pass

    def process_response(self, request, response):

        path = request.path
        if not path or not path.startswith(API_PREFIX_NAME) or path in ignore_path:
            return response

        # request_id = request.META.get("HTTP_X_REQUEST_ID", '')
        request_id = getattr(request, 'x_request_id')
        if request_id is None:
            request_id = str(uuid.uuid4())

        log_msg = {
            "transform": "response",
            'path': path,
            'request_id': request_id,
            'method': request.method,
            'scheme': request.scheme,
            'status_code': response.status_code,
            'status_text': getattr(response, 'status_text', None) or None,
            'response': getattr(response, 'data', None) or None,
        }
        if request_id:
            response['X-PL-REQUEST-ID'] = str(request_id)

        try:
            logger.info(json.dumps({"msg": log_msg, "tag": ["api-middleware", "process_response"]}, ensure_ascii=False))
        except:
            pass

        return response


class RenameThreadWithUUID4(MiddlewareMixin):

    def process_request(self, request):
        t = threading.current_thread()
        new_name = uuid.uuid4()
        t.name = str(new_name)


class SignatureInvalid(Exception):

    def __init__(self, msg, request, *args: object):
        super().__init__(msg, request, *args)
        # fmt_error(log=logger, title="鉴权异常", e=self, other="", request=request)
        log_signature.warning(
            {
                "msg": f'请求路径: {request.path} 签名校验错误-{msg}!',
                "header": f"{dict(request.META)}",
                "request_id": request.META.get("HTTP_X_REQUEST_ID", ""),
                "tag": ["api-middleware", "SignatureInvalid"],
            }
        )


# 需要验证签名的后台 Api set
ignore_urls_set = {
    "/api/",
}

# 不需要签名验证的API路径前缀
ignore_signature_paths = {
    "/api/survey/external/commitlog",
}

APiSignatureMiddleware = SignatureHelper(logger=log_signature)


class ApiSignatureMiddleware(MiddlewareMixin):
    # python -c "import random, string; print(''.join(random.choices(string.ascii_letters + string.digits, k=32)))"
    APP_SECRET = 'ZEzLu5r0gA1j8kg8h6c92gxFElKcDAjm'
    APP_ID = 'Y8G3SoOVLfbwh7mZNySDL69jMoFWqamH'

    def validate_signature(self, request):
        _meta = request.META

        x_appid, x_timestamp, x_nonce_str, x_signature = _meta.get('HTTP_X_APPID', ""), \
            _meta.get('HTTP_X_TIMESTAMP', ""), _meta.get('HTTP_X_NONCESTR', ""), _meta.get('HTTP_X_SIGNATURE', "")
        x_client_version, x_client_source, x_api_version = _meta.get('HTTP_X_CLIENT_VERSION', ""), \
            _meta.get('HTTP_X_CLIENT_SOURCE', ""), _meta.get('HTTP_X_API_VERSION', "")

        logger.info({
            "x_appid": x_appid,
            "x_timestamp": x_timestamp,
            "x_nonce_str": x_nonce_str,
            "x_signature": x_signature,
            "x_client_version": x_client_version,
            "x_client_source": x_client_source,
            "x_api_version": x_api_version,
        })

        if not all([x_appid, x_timestamp, x_nonce_str, x_signature, x_client_version, x_client_source, x_api_version]):
            raise SignatureInvalid('Invalid token params.', request)
        try:
            x_timestamp = int(x_timestamp)
        except Exception:
            raise SignatureInvalid('Invalid timestamp.', request)

        if not APiSignatureMiddleware.validate_params(
                x_appid, self.APP_SECRET, x_nonce_str, x_timestamp, x_signature,
                x_client_version, x_client_source, x_api_version
        ):
            raise SignatureInvalid('Invalid token .', request)

    def process_request(self, request: HttpRequest):
        
        # 检查是否是不需要签名验证的路径
        for ignore_path in ignore_signature_paths:
            if request.path.startswith(ignore_path.rstrip('/')):
                return None

        survival = [
            target_url for target_url in ignore_urls_set if
            target_url in request.path and ('/api/user/wechatCallback/' not in request.path)
        ]
        if len(survival) > 0:
            try:
                self.validate_signature(request)
            except SignatureInvalid as e:
                signature_id = str(uuid.uuid4())
                log_signature.warning(
                    {
                        "msg": f'Signature Exception: {request.path} 签名校验错误-{e}!',
                        "signature_id": signature_id,
                        'headers': f"{dict(request.META)}",
                        "tag": ["api-middleware", "ApiSignatureMiddleware"],
                    }
                )
                return HttpResponseForbidden(
                    f'Invalid Signature-Token {f": {e.args[0]}" if len(e.args) > 0 else ""} - {signature_id}'
                )

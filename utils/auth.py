import logging
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from utils.fmt_log_exception import fmt_error
from utils.signature import APiSignature

log_default = logging.getLogger("user_log")


class OPENDing(BaseAuthentication):
    """
    open api
    """
    app_secret = "123"

    def authenticate(self, request):
        _meta = request.META

        x_appid, x_timestamp, x_nonce_str, x_signature = _meta.get('HTTP_X_APPID', ""), \
            _meta.get('HTTP_X_TIMESTAMP', ""), _meta.get('HTTP_X_NONCESTR', ""), _meta.get('HTTP_X_SIGNATURE', "")
        x_client_version, x_client_source, x_api_version = _meta.get('HTTP_X_CLIENT_VERSION', ""), \
            _meta.get('HTTP_X_CLIENT_SOURCE', ""), _meta.get('HTTP_X_API_VERSION', "")

        log_default.info({
            "x_appid": x_appid,
            "x_timestamp": x_timestamp,
            "x_nonce_str": x_nonce_str,
            "x_signature": x_signature,
            "x_client_version": x_client_version,
            "x_client_source": x_client_source,
            "x_api_version": x_api_version,
        })

        if not all([x_appid, x_timestamp, x_nonce_str, x_signature, x_client_version, x_client_source, x_api_version]):
            raise AuthenticationFailed(_('Invalid token params.'))
        try:
            x_timestamp = int(x_timestamp)
        except Exception as e:
            fmt_error(log=log_default, title="鉴权异常", e=e, other="信息补充字段", request=request)
            raise AuthenticationFailed(_('Invalid timestamp.'))

        if not APiSignature.validate_params(
                x_appid, self.app_secret, x_nonce_str, x_timestamp, x_signature,
                x_client_version, x_client_source, x_api_version
        ):
            raise AuthenticationFailed(_('Invalid token .'))

        return None, None

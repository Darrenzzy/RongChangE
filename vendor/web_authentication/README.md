## 工具包

### 1. API 数字签名 认证

```
utils.signature.SignatureHelper

demo tests:

    user.tests.ApiSignatureCase.test_signature

```

* 使用方式

```python

from django.utils.translation import ugettext_lazy as _

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from utils.signature import APiSignature


class OPENDing(BaseAuthentication):
    """
    open api
    """
    
    app_secret = "123"

    def authenticate(self, request):
        _meta = request.META

        x_appid, x_timestamp, x_nonce_str, x_signature = _meta.get('HTTP_X_APPID', ""),
            _meta.get('HTTP_X_TIMESTAMP', ""), _meta.get('HTTP_X_NONCESTR', ""), _meta.get('HTTP_X_SIGNATURE', "")
        x_client_version, x_client_source, x_api_version = _meta.get('HTTP_X_CLIENT_VERSION', ""),
            _meta.get('HTTP_X_CLIENT_SOURCE', ""), _meta.get('HTTP_X_API_VERSION', "")

        if not any([x_appid, x_timestamp, x_nonce_str, x_signature, x_client_version, x_client_source, x_api_version]):
            raise AuthenticationFailed(_('Invalid token params.'))
        try:
            x_timestamp = int(x_timestamp)
        except Exception as e:
            raise AuthenticationFailed(_('Invalid timestamp.'))

        # 校验失败
        if not APiSignature.validate_params(
                x_appid, self.app_secret, x_nonce_str, x_timestamp, x_signature,
                x_client_version, x_client_source, x_api_version
        ):
            raise AuthenticationFailed(_('Invalid token .'))

        return None, None


# use api signature OPENDing Authentication
class User(GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    queryset = User.objects.all()
    authentication_classes = [OPENDing, ]

# reference: 
# user.views.User
```

* 规则：

  参与签名字段
| field | description  |  remark   |
|--|-----|-----|
| x_appid  |  签名用户信息主体字段键名   |     |
| x_timestamp |  签名参与计算的 13位时间戳 精确到ms   | 默认3分钟的有效期时延，即 请求后该签名在三分钟内才有效, 实际以后端开发为准。 |
| x_nonce_str | 签名参与计算的 随机字符串 |     |
| x_signature | sign签名数据值 | 由 x-appid、x-timestamp、x-noncestr、x-client-version、x-client-source、x-api-version 字段经过 参数名ASCII字典序排序 得到 字符串，并且通过 & 拼接得到的签名字符串 sign_str ，如 sign_str = 'x-api-version={api_version}&x-appid={x-appid}&x-client-source={x-client-source}&x-client-version={x-client-version}&x-noncestr={x-noncestr}&x-timestamp={x-timestamp}'. 再使用 md5({sign_str}&key={app_secret}).lower() 得到最终的签名值 x-signature. |
| x_client_version | 签名参与计算的 客户端版本 | 如 安卓版本、浏览器版本号 ... |
| x_client_source | 签名参与计算的 客户端来源 | 如 安卓、苹果、xxx浏览器 ... |
| x_api_version | 签名参与计算的 服务端api版本号 | 如 V1、V2 ... |
| app_secret | 颁发至参与签名的密钥 | 由后端颁发生成 |


* demo :
```
 {
    'x-appid': 'openid',  # 具体业务而定， 如微信可以是微信用户的openid
    'x-timestamp': '1670496306500',  # 精确到毫秒的 13位 时间戳
    'x-noncestr': 'zdSzz09vKaI63aq',  # 随机字符串
    'x-client-version': 'client_version',  # 客户端版本，可以是 手机机型版本
    'x-client-source': 'client_source',  # 客户端来源  可以是机型  如安卓 苹果
    'x-api-version': 'api_version',  # api 接口版本，视具体开发而定
    'x-signature': 'de10b3379c7098b18fa147e128c10944'
    
    # x-signature 该字段值由上述 x-appid、x-timestamp、x-noncestr、x-client-version、x-client-source、x-api-version 字段经过 参数名ASCII字典序排序 得到 字符串 并且通过 & 拼接得到的签名字符串 _sign_str , 再使用 md5({_sign_str}&{app_secret}) 得到最终的签名值 x-signature，
    # 参考如下：[ app_secret = 123 ]
    # x-api-version=api_version&x-appid=openid&x-client-source=client_source&x-client-version=client_version&x-noncestr=01TZE9w2JcWmJMq&x-timestamp=1670496709703
    # 得到的 'x-signature': 'd6f495da041fc9f3754e0fed8cbab061'
}

```





### json 日志 适配 线上日志查询
```python 
import json

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # 一般 格式日志文件
        'standard': {
            'format': '%(asctime)s %(threadName)s [%(name)s:%(module)s.%(funcName)s:%(lineno)d] '
                      '[%(levelname)s] - %(message)s',
        },
        # json 格式日志文件
        "json": {
            'format': json.dumps(
                {
                    "asctime": "%(asctime)s",
                    "threadName": "%(threadName)s",
                    "fullpath": "%(pathname)s:%(lineno)d",
                    "name": "%(name)s:%(module)s.%(funcName)s:%(lineno)d",
                    "levelname": "%(levelname)s",
                    "message": "%(message)s"
                }
            )
        }
    },

    'handlers': {
        'user_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './logs/user_log.log',
            'maxBytes': 1024 * 1024 * 5 * 100,
            'backupCount': 5,
            'formatter': 'json',  # json 日志格式
        },
    },

    'loggers': {
        'user_log': {
            'handlers': ['user_log', ],
            'level': 'DEBUG',
            'propagate': True
        },
    },
}

# usage

import logging

log_default = logging.getLogger("user_log")

log_default.info(
    {
        "x_appid": "",
        "x_timestamp": "",
        "x_nonce_str": "",
        "x_signature": "",
        "x_client_version": "",
        "x_client_source": "",
        "x_api_version": "",
    }
)

```

* result: 
```json
{
  "asctime": "2023-04-03 18:46:08,935",
  "threadName": "Thread-2 (process_request_thread)",
  "fullpath": "F:\GitSpace\django3demo\utils\auth.py:27",
  "name": "user_log:auth.authenticate:27",
  "levelname": "INFO",
  "message": "{'x_appid': '', 'x_timestamp': '', 'x_nonce_str': '', 'x_signature': '', 'x_client_version': '', 'x_client_source': '', 'x_api_version': ''}"
}
```

* 日志异常捕获堆栈入文件：
`utils.fmt_log_exception.fmt_error`
  * 目前存在bug，设计不够完善，将信息作为字符串写入日志中的message， message可能会存在由于双引号  单引号等非转义符号导致形成非json格式数据。
  * 目前简单处理方式：  replace 相关字符
``` 

def fmt_error(log, title, e, other='', request=None):
    """
    提取 Log Error 错误栈

    :param log:     log instance eg: log_validate = logging.getLogger("validate")
    :param title:   log 标题
    :param e:       log 错误栈 Exception
    :param other:   log 辅助性描述
    :param request: django request 辅助性描述
    :return:
    """

    traceback_format = replace_space(default_filter_str, traceback.format_exc())
    log.error(
        {
            "error_type": replace_space(default_filter_str, f"{type(e)}"),
            "error_message": replace_space(default_filter_str, str(e)),
            "other": replace_space(default_filter_str, other),
            "title": f"{settings.PROJECT_NAME}-{settings.TOP_DOMAIN}",
            "error_uri": f"当前请求异常路径uri={request.build_absolute_uri()}" if request is not None else "",
            "traceback": traceback_format,
        }
    )
    if settings.DEBUG:
        # print error traceback
        print("===================== START  {0},错误={1}, {2}  START =====================".format(title, e, other))
        traceback.print_exc()

    else:
        # new thread send email error log
        thr = Thread(target=core_send_mail,
                     args=(title, traceback.format_exc(), settings.DEFAULT_FROM_EMAIL, [settings.ADMINS[0][1]]))
        thr.start() 
        

# usage
        try:
            x_timestamp = int(x_timestamp)
        except Exception as e:
            fmt_error(log=log_default, title="鉴权异常", e=e, other="信息补充字段", request=request)
            raise AuthenticationFailed(_('Invalid timestamp.'))
            
```

* result：
```json
{
  "asctime": "2023-04-03 19:08:23,506",
  "threadName": "Thread-1 (process_request_thread)",
  "fullpath": "F:\GitSpace\django3demo\utils\fmt_log_exception.py:45",
  "name": "user_log:fmt_log_exception.fmt_error:45",
  "levelname": "ERROR",
  "message": "{'error_type': '<class ValueError>', 'error_message': 'invalid literal for int() with base 10: ', 'other': '信息补充字段', 'title': 'django-undefined-your-site-domain', 'error_uri': '当前请求异常路径uri=http://127.0.0.1:8000/api/user/', 'traceback': 'Traceback (most recent call last):  File F:\\GitSpace\\django3demo\\utils\\auth.py, line 40, in authenticate    x_timestamp = int(x_timestamp)ValueError: invalid literal for int() with base 10: '}"
}

```
* demo:
`utils/auth.py:27` `utils.fmt_log_exception.fmt_error`

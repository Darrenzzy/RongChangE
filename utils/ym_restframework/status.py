#!/usr/bin/env python
# -*- coding: utf-8 -*-


import inspect
import sys
from http.client import responses

from rest_framework.status import is_success


class BaseHttpStatus:
    status = None
    message = None


class HTTP_4200_OK(BaseHttpStatus):
    status = 0
    message = "成功"


class HTTP_4201_CREATED(BaseHttpStatus):
    status = 0
    message = "成功创建"


class HTTP_4202_ACCEPTED(BaseHttpStatus):
    status = 0
    message = "可接受"


class HTTP_4203_NON_AUTHORITATIVE_INFORMATION(BaseHttpStatus):
    status = 0
    message = "非权威信息"


class HTTP_4204_NO_CONTENT(BaseHttpStatus):
    status = 0
    message = "无内容"


class HTTP_4205_RESET_CONTENT(BaseHttpStatus):
    status = 0
    message = "内容重置"


class HTTP_4206_PARTIAL_CONTENT(BaseHttpStatus):
    status = 0
    message = "部分内容"


class HTTP_4207_MULTI_STATUS(BaseHttpStatus):
    status = 0
    message = "多状态"


class HTTP_4208_ALREADY_REPORTED(BaseHttpStatus):
    status = 0
    message = "已报告"


class HTTP_4226_IM_USED(BaseHttpStatus):
    status = 0
    message = "即时通信被使用"


class HTTP_4300_MULTIPLE_CHOICES(BaseHttpStatus):
    status = 4300


class HTTP_4301_MOVED_PERMANENTLY(BaseHttpStatus):
    status = 4301


class HTTP_4302_FOUND(BaseHttpStatus):
    status = 4302


class HTTP_4303_SEE_OTHER(BaseHttpStatus):
    status = 4303


class HTTP_4304_NOT_MODIFIED(BaseHttpStatus):
    status = 4304


class HTTP_4305_USE_PROXY(BaseHttpStatus):
    status = 4305


class HTTP_4306_RESERVED(BaseHttpStatus):
    status = 4306


class HTTP_4307_TEMPORARY_REDIRECT(BaseHttpStatus):
    status = 4306


class HTTP_4308_PERMANENT_REDIRECT(BaseHttpStatus):
    status = 4308


class HTTP_4400_BAD_REQUEST(BaseHttpStatus):
    status = 4400
    message = "请求错误"


class HTTP_4401_UNAUTHORIZED(BaseHttpStatus):
    status = 4401
    message = "未认证"


class HTTP_4402_PAYMENT_REQUIRED(BaseHttpStatus):
    status = 4402
    message = "付费之后才能获取"


class HTTP_4403_FORBIDDEN(BaseHttpStatus):
    status = 4403
    message = "访问禁止"


class HTTP_4404_NOT_FOUND(BaseHttpStatus):
    status = 4404
    message = "未找到"


class HTTP_4405_METHOD_NOT_ALLOWED(BaseHttpStatus):
    status = 4405
    message = "方法不被允许"


class HTTP_4406_NOT_ACCEPTABLE(BaseHttpStatus):
    status = 4406
    message = "不可接受的"


class HTTP_4407_PROXY_AUTHENTICATION_REQUIRED(BaseHttpStatus):
    status = 4407
    message = "需要代理身份认证"


class HTTP_4408_REQUEST_TIMEOUT(BaseHttpStatus):
    status = 4408
    message = "请求超时"


class HTTP_4409_CONFLICT(BaseHttpStatus):
    status = 4409
    message = "冲突"


class HTTP_4410_GONE(BaseHttpStatus):
    status = 4410


class HTTP_4411_LENGTH_REQUIRED(BaseHttpStatus):
    status = 4411


class HTTP_4412_PRECONDITION_FAILED(BaseHttpStatus):
    status = 4412


class HTTP_4413_REQUEST_ENTITY_TOO_LARGE(BaseHttpStatus):
    status = 4413


class HTTP_4414_REQUEST_URI_TOO_LONG(BaseHttpStatus):
    status = 4414


class HTTP_4415_UNSUPPORTED_MEDIA_TYPE(BaseHttpStatus):
    status = 4415


class HTTP_4416_REQUESTED_RANGE_NOT_SATISFIABLE(BaseHttpStatus):
    status = 4416


class HTTP_4417_EXPECTATION_FAILED(BaseHttpStatus):
    status = 4417


class HTTP_4418_IM_A_TEAPOT(BaseHttpStatus):
    status = 4418


class HTTP_4422_UNPROCESSABLE_ENTITY(BaseHttpStatus):
    status = 4422


class HTTP_4423_LOCKED(BaseHttpStatus):
    status = 4423


class HTTP_4424_FAILED_DEPENDENCY(BaseHttpStatus):
    status = 4424


class HTTP_4426_UPGRADE_REQUIRED(BaseHttpStatus):
    status = 4426


class HTTP_4428_PRECONDITION_REQUIRED(BaseHttpStatus):
    status = 4428


class HTTP_4429_TOO_MANY_REQUESTS(BaseHttpStatus):
    status = 4429
    message = "操作频繁，请稍后再试"


class HTTP_4431_REQUEST_HEADER_FIELDS_TOO_LARGE(BaseHttpStatus):
    status = 4431
    message = "请求头字段过长"


class HTTP_4450_CUSTOM_TEXT(BaseHttpStatus):
    status = 4450
    message = "请求错误"


class HTTP_4451_UNAVAILABLE_FOR_LEGAL_REASONS(BaseHttpStatus):
    status = 4451
    message = "无法提供法律依据"


class HTTP_4459_WX_NOT_AUTH(BaseHttpStatus):
    status = 4459
    message = "微信未授权"


class HTTP_4460_NOT_ATTENTION(BaseHttpStatus):
    status = 4460
    message = "用户未关注"


class HTTP_4461_NOT_REGISTER(BaseHttpStatus):
    status = 4461
    message = "用户未注册"


class HTTP_4462_NOT_SECOND_REGISTER(BaseHttpStatus):
    status = 4462
    # message = "用户未二次认证"
    message = "用户 {openid} 未二次认证"


class HTTP_4470_UPPER_LIMIT_INTEGRAL(BaseHttpStatus):
    status = 4470
    message = "您累计兑换积分已达到{0}分，<br/>邀请您前往完成二次认证，<br/>再进行后续兑换，<br/>非常感谢您的支持！"


class HTTP_4470_MONTH_UPPER_LIMIT_INTEGRAL(BaseHttpStatus):
    status = 4470
    message = "您本月累计兑换积分已达到{0}分，<br/>邀请您前往完成二次认证，<br/>再进行后续兑换，<br/>非常感谢您的支持！"


class HTTP_4471_NOT_EMAIL(BaseHttpStatus):
    status = 4471
    message = "请完善邮箱信息"


class HTTP_4472_NOT_ADDRESS(BaseHttpStatus):
    status = 4472
    message = "请填写收货地址后再提交"


class HTTP_4500_INTERNAL_SERVER_ERROR(BaseHttpStatus):
    status = 4500
    message = "服务器内部错误"


class HTTP_4501_NOT_IMPLEMENTED(BaseHttpStatus):
    status = 4501
    message = "不可执行"


class HTTP_4502_BAD_GATEWAY(BaseHttpStatus):
    status = 4502
    message = "错误网关"


class HTTP_4503_SERVICE_UNAVAILABLE(BaseHttpStatus):
    status = 4503
    message = "服务器无效"


class HTTP_4504_GATEWAY_TIMEOUT(BaseHttpStatus):
    status = 4504
    message = "网关超时"


class HTTP_4505_HTTP_VERSION_NOT_SUPPORTED(BaseHttpStatus):
    status = 4505
    message = "http版本不支持"


class HTTP_4506_VARIANT_ALSO_NEGOTIATES(BaseHttpStatus):
    status = 4506


class HTTP_4507_INSUFFICIENT_STORAGE(BaseHttpStatus):
    status = 4507


class HTTP_4508_LOOP_DETECTED(BaseHttpStatus):
    status = 4508


class HTTP_4509_BANDWIDTH_LIMIT_EXCEEDED(BaseHttpStatus):
    status = 4509


class HTTP_4510_NOT_EXTENDED(BaseHttpStatus):
    status = 4510


class HTTP_4511_NETWORK_AUTHENTICATION_REQUIRED(BaseHttpStatus):
    status = 4511


# 以“HTTP_44xx: StautsClass”组成字典数据，方便查询

_status_class_mapping = {}

filter_class = (
    lambda obj: inspect.isclass(obj)
    and issubclass(obj, BaseHttpStatus)
    and obj.status is not None
)
for name, class_ in inspect.getmembers(sys.modules[__name__], filter_class):
    _status_class_mapping[name[0:9]] = class_


# 根据原始status_code查询转化的状态码
def get_status_class(status_code):

    status = 4000 + status_code
    status_class = _status_class_mapping.get(f"HTTP_{status}")
    if status_class:
        return status_class

    if is_success(status_code):
        status = 0
    message = responses.get(status_code, None)

    # 如果没有查询到预期的StatusClass，则临时创建一个通用的StatusClass
    PublicStatusClass = type(
        "PublicStatusClass",
        (BaseHttpStatus,),
        {
            "status": status,
            "message": message,
        },
    )

    return PublicStatusClass

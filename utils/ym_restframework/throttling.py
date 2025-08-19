#!/usr/bin/env python
# -*- coding: utf-8 -*-


from rest_framework.throttling import SimpleRateThrottle

"""
throttle 节流

rest_framework.throttling.SimpleRateThrottle 节流原理:
    10/m => 一个标识用户1分钟限制了10次请求，10次请求可以没有间隔，
    就是说，我在1s内完成了10次请求，接下来的59s请求被限制
    此类不会被直接引用，通常被继承后，定义 scope 值和 THROTTLE_RATES 值

rest_framework.throttling.AnonRateThrottle: 
    scope = 'anon'， 匿名用户节流类， 使用request.ip唯一标识

rest_framework.throttling.UserRateThrottle: 
    scope = 'user'， 认证用户节流类， 使用user.id唯一标识

rest_framework.throttling.ScopedRateThrottle: 
    scope = {throttle_scope}， 使用 throttle_scope 属性针对不同views作不同的限流，
    只有在views中配置了 throttle_scope 才会生效

settings.py 配置如下:
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    # s, m, h, d
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/s',
        'user': '30/s',
    }
}
"""


class AverageRateThrottle(SimpleRateThrottle):
    """
    为了请求之间有间隔，我们要重新定义下限制规则，即重写 def allow_request()
    eg: 10/s => 1分钟10次请求限制，第1次请求后，下次要求6s之后
    """

    scope = "public"

    def allow_request(self, request, view):
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        self.avg_time = round(self.duration / self.num_requests, 7)
        if self.history and self.history[0] >= self.now - self.avg_time:
            return self.throttle_failure()
        self.history = []
        return self.throttle_success()

    def wait(self):
        """返回下次请求的建议时间"""

        if not hasattr(self, "avg_time"):
            self.avg_time = 0

        remaining_duration = None
        if self.history:
            remaining_duration = self.avg_time - (self.now - self.history[0])
        return remaining_duration

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}

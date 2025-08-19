#!/usr/bin/env python
# -*- coding: utf-8 -*-


def initialize_request(self, request, *args, **kwargs):
    """
    viewsets.ViewSetMixin
    在 initialize_request 之前初始化action数据，
    这样的话，方法 get_authenticators() 可以使用 self.action
    Set the `.action` attribute on the view, depending on the request method.
    """
    method = self.request.method.lower()
    if method == "options":
        # This is a special case as we always provide handling for the
        # options method in the base `View` class.
        # Unlike the other explicitly defined actions, 'metadata' is implicit.
        self.action = "metadata"
    else:
        self.action = self.action_map.get(method)
    request = super(self.__class__, self).initialize_request(request, *args, **kwargs)
    return request

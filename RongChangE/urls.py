"""RongChangE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path

import xadmin

urlpatterns = [
    # xamdin后台
    path(r"xadmin/", xadmin.site.urls),
    # 富文本编辑器
    path(r"ueditor/", include("DjangoUeditor.urls")),
    path(r"api/user/", include("user.urls")),
    path(r"api/agreement/", include("agreement.urls")),
    path(r"api/work/", include("works.urls")),
    path(r"api/survey/", include("survey.urls")),

    # health_check
    path(r"", include("vendor.health_check.urls"), ),
]

# 下面的静态文件服务和媒体文件服务不适合在生产环境使用
# 当DEBUG=False时，下面的路由是无效的
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = [
                      re_path(r'^__debug__/', include(debug_toolbar.urls)),

                      # For django versions before 2.0:
                      # url(r'^__debug__/', include(debug_toolbar.urls)),

                  ] + urlpatterns

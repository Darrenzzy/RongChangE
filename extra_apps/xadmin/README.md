# 适配django3.x的xadmin

## 安装

1. 安装requeirements.txt里面的包

```
pip install xadmin\requirements.txt
```

2. 相应app加到INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ...
    "xadmin",
    "crispy_forms",
    "crispy_bootstrap3",
    'reversion',  # 请使用本地依赖文件，存在代码优化 
    # ...
]

# crispy_forms 1.9.2 以后进行抽离，必须单独install crispy_bootstrap3 并在settings中指定bootstrap版本
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap3"
CRISPY_TEMPLATE_PACK = "bootstrap3"

```

3. 应用迁移脚本

```pyhton
python manage.py migrate
```

## 其他问题

1. ueditor图片加载不出来

xxx/urls.py加配置

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

2. ueditor里面上传图片时报“上传失败”，f12控制台错误“`in a frame because it set 'X-Frame-Options' to 'deny'.`”

在xxx/settings.py加配置

参考：https://blog.csdn.net/ora_dy/article/details/104984482

```python
X_FRAME_OPTIONS = "SAMEORIGIN"
```


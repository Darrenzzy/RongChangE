## 七牛云 上传字段

### `QiniuField`
* 安装七牛云SDK
```
pip install qiniu
```

* `settings` 文件配置七牛云参数:
  * `QINIU_ACCESS_KEY`: 七牛云 AK
  * `QINIU_SECRET_KEY`: 七牛云 SK
  * `QINIU_DOMAIN`: 七牛云 域名
  * `QINIU_BUCKET_NAME`:  七牛云 bucket name
* demo:
```
# settings.py
INSTALLED_APPS = [
  ...,
  
  'qiniuupload',  # 七牛云上传
  
  ...,
]


# 七牛云参数配置
QINIU_ACCESS_KEY = 'xxx'
QINIU_SECRET_KEY = 'xxx'
QINIU_DOMAIN = 'http|s://xxx.xxx.xxx'
QINIU_BUCKET_NAME = 'xxx'


# models.py
from django.db import models
from qiniuupload.fields import QiniuField

class User(models.Model):
    ...
    pic = QiniuField(verbose_name="七牛云图片地址", max_length=600, help_text="请等待上传成功后在保存哦~")

```

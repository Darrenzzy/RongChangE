CHANGELOG:
### 2024-02-01
1. 优化x-admin导出思路
* 在 `get_response` 函数中取 `request`属性函数`export_view`
![export-response.png](docs%2Fimages%2Fexport-response.png)

* 在 `x-admin` `querytset` 生命周期中将`export_view` 赋予给 `request`
* 再实现 `export_view` 函数查询，可在原有查询中篡改`select`部分。
![export-view.png](docs%2Fimages%2Fexport-view.png)


### 2023-12-28
1. x-admin 新增`CharField`字符串多图片url预览插件功能
   - `xadmin.plugins.images.CharFieldImagePreviewPlugin`
   - `style_fields = {"xxx": "preview"}`
   - 手动支持字符串多图片url预览: `user.adminx.UserAdmin.result_item`
   - 暂未支持 七牛云上传字段预览 `QiniuField`，替补方案`七牛云列表字段多图urls预览` - `extra_apps/xadmin/views/list.py:619`,支持列表时若资源为图片时自动开启预览，支持多图，但不支持详细页面预览
2. x-admin 多选 checkbox 插件支持
   - `xadmin\plugins\checkbox.py`

### 2023-7-14
1. x-admin增加save_after
   - xadmin.views.edit.ModelFormAdminView类中
   - 为解决save_models()后其关联对象暂未保存，导致直接获取却获取不到其关联对象的问题，亦可追加其他操作
   - 使用方式：
      ```
     def save_after(self):
        # 判断是否是新增
        created = self.org_obj is None or False
        # 新增发送站内信给指定用户
        if created:
            # 获取关联用户对应的openid
            openids = self.new_obj.users.filter(is_delete=False, active=True).values_list("openid", flat=True).all()
            # 发送系统模板消息
            send_template_system.delay(openids=openids, content=self.new_obj.content,date_time=self.new_obj.time_create.strftime('%Y年%m月%d %H:%M'),path=f'/pages/msg/detail?id={self.new_obj.pk}')
     ```
   

### 2023-6-05

1. x-admin 新增 widget
   * `xadmin.widgets.AdminRemoteSelectWidget`
   * 该 widget 解决ForeignKey数据过大导致 x-admin detail 页面渲染外键数据卡顿
   * 使用方式：
    ```
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "hospital":
            kwargs["widget"] = AdminRemoteSelectWidget(api_uri="/xadmin/hospital-nest/")
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, **kwargs)
   
   
    # api_uri 需要支持模糊过滤search  和 pk 精确检索功能
    # demo
    from xadmin.sites import register_view as xadmin_register_view
   
    @xadmin_register_view(r'^hospital-nest/$', 'hospital-nest')
    class HospitalNestView(BaseAdminView):
        def get(self, request, *args, **kwargs):
            pk = request.GET.get("pk")
            if pk:
                try:
                    obj = Hospital.objects.get(pk=int(pk))
                    return JsonResponse({"data": [{"id": obj.pk, "name": obj.title}]})
                except Exception as e:
                    return JsonResponse({"data": []]})

            search = request.GET.get("search")
            if search:
               objs = Hospital.objects.filter(title__icontains=search).values("pk", "title")[:1000]
               return JsonResponse({"list": [{"id": obj['pk'], "name": obj['title']} for obj in objs]})
            
            objs = Hospital.objects.values("pk", "title")[:1000]
            return JsonResponse({"list": [{"id": obj['pk'], "name": obj['title']} for obj in objs]})
   
    ```

2. fix `django-crispy-forms` bug： render context
3. x-admin 新增参数功能 `xadmin/views/list.py:123`
   ``` 
   # 新增按钮
   button_urls = [{"link": "https://www.baidu.com", "title": "百度"}]
   ```

### 2023-4-26
 
1. 优化调整日志模块，新增 `xadmin_log` `data` 字段， 用于存储删除、修改、新增数据的历史数据。
   * 支持 xadmin 初次 migrate 建表操作
   * 若是后续追加的该模块，建议手动将 `data` 字段作用到表结构上。
2. `data` 字段 不可编辑。
3. 日志记录 `message` 字段剥离删除的信息，转存在 `data` 字段。
4. 适配x-admin delete、edit、create hook 函数
5. 优化权限信号量 migrate 查询操作 `xadmin/model/add_view_permissions`。



### 2023-4-25

1. x-admin plugin auth.py get_permission_name函数 数据库 N+N 问题优化。
2. x-admin login & logout forms.py 支持自定义部分业务，如 登入登出的日志，单用户同一时间内单设备登入验证控制示例代码。
3. x-admin login & logout signals 示例代码



### 2023-04-23
1. x-admin 后台login追加登入校验
2. 完成 django 4.2 适配
   * 详情请见 [changelog.django.4.2.md](changelog.django.4.2.md)
3. 优化 x-admin 权限组sql遍历问题
```text
def cache_orm_content_type(content_type_id: int) -> str:
    # https://docs.djangoproject.com/zh-hans/4.2/ref/settings/#caches
    local_cache = settings.CACHES.get("default", None)
    if local_cache is None:
        settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

    cache_name = "orm_ctx_type_query_result"

    result = cache.get(cache_name, {})
    if not result:
        result = {x.pk: x.app_labeled_name for x in ContentType.objects.all()}
        cache.set(cache_name, result, timeout=3)
    return result.get(content_type_id, "-")


def get_permission_name(p):
    action = p.codename.split('_')[0]
    if action in ACTION_NAME:
        # return ACTION_NAME[action] % str(p.content_type)
        return ACTION_NAME[action] % str(cache_orm_content_type(p.content_type_id))
    else:
        return p.name
```


### 2023-4-3

1. export 异常支持 `xadmin.plugins.export.ExportPlugin.get_response`
2. list view 参数过滤异常拦截处理 `xadmin.views.list.ListAdminView.get_list_queryset`
3. search 支持加密字段的模糊搜索中的指定字段精确匹配 `xadmin/plugins/filters.py:191`


### 20230-2-3

1. debug=false时， x-admin view list 捕获异常message提示
2. list editable & filter & sort able list 修复bug
3. excel 插件支持配置导入的excel模板下载功能
4. 部分优化


### 2022-12-21

1. BookMark 默认关闭, `extra_apps/xadmin/plugins/bookmark.py:30`
2. export 导出功能 颗粒化 后台权限控制
    1. migrate signal 支持新增 export 权限 `xadmin.models.add_view_permissions:35`
    2. export 导出按钮 权限设计 `xadmin.views.base.BaseAdminPlugin.has_export_permission:53`
    3. export 导出功能 权限设计 `xadmin.plugins.export.ExportPlugin.init_request:79`
    4. 管理员默认开启 export 功能，非管理员需要靠权限分配
    5. 导出插件权限与 export 同步 `extra_apps/xadmin/plugins/actions.py:348`

3. Log x-admin 配置页面 remove_permissions 效率不佳，使用固定函数替换

### 2022-12-09

1. 支持 AES 加密model字段 `xadmin/expand_model_fields.py`
2. 加密字段配置搜索 `extra_apps/xadmin/plugins/filters.py:37`
3. AES tool `xadmin/ase_helper.py`
4. 优化 x-admin 自定义下载插件的 下载提示页面数据sql
5. demo :
   ``` 
   user.models.User
   apps/user/adminx.py:38
   ```

### 2022-12-08

1. 修复集成 x-admin plugin reversion;
    1. 全局默认开启model数据版本插件按钮;
    2. reference extra_apps/xadmin/plugins/xversion.py:162
    3. 自定义修改 reversion 源码，优化查询、禁用相关权限;
2. 优化 x-admin 内置表的查询;
3. x-admin log 数据序列化深度 extract_map 优化;

### 2022-12-05

1. 优化 x-admin Excel 表格导出行数65536上线问题，自带分页计算导出；
    1. 参考： `extra_apps/xadmin/plugins/export.py:126`
2. 导出插件集成 数据隐私 tips & 导出日志记录；
    1. 参考： `extra_apps/xadmin/plugins/export.py:42`
    2. 参考： `xadmin.views.base.BaseAdminObject.log`
3. x-admin log 优化查询、权限禁用delete|create|change；
    1. 参考： `extra_apps/xadmin/adminx.py:20`
4. 新增 自定义导出 action，优化查询导出方式；
    1. 优点： 加速查询下载，提升导出性能、且只关注sql构建，提供pandas.DataFrame即可；
    2. 缺点：只能导出固定的表格表格，无法适配 x-admin excel 任意字段的指定；
    3. 参考 `apps.user.adminx.UserAdmin.to_download`
    4. 参考 `xadmin.plugins.actions.CustomDownAction`
5. 日志模块修复 ip-address 无法读取实际ip-address问题；
    1. 参考: `extra_apps/xadmin/views/base.py:228`
6. 优化 x-admin 用户、权限表查询；
    1. 参考: `extra_apps/xadmin/adminx.py:20`

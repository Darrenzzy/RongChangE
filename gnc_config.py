#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime

import psutil

__doc = """

    reference: 
        - https://docs.gunicorn.org/en/stable/

        - https://blog.csdn.net/kuanggudejimo/article/details/103713302?spm=1001.2101.3001.6650.15&utm_medium=distribute.pc_relevant.none-task-blog-2~default~BlogCommendFromBaidu~default-15.no_search_link&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2~default~BlogCommendFromBaidu~default-15.no_search_link
"""

# 项目目录为当前文件的上一级
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 项目目录

reload_dirs = BASE_DIR

LOG_ROOT = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_ROOT):
    os.makedirs(LOG_ROOT)

sys.path.insert(0, BASE_DIR)

# 指定监听的地址和端口，这里使用nginx转发了，所以监听特殊端口
bind = '0:8000'

proc_name = 'gunicorn_RongChangE'

chdir = BASE_DIR

# 代码更新时重启项目
reload = True

# debug = True

# 不守护Gunicorn进程
daemon = False

# 服务器中排队等待的最大连接数，建议值64-2048，超过2048时client连接会得到一个error。
backlog = 2048

# worker_class = 'sync'
worker_class = "uvicorn.workers.UvicornWorker"

# 用于处理工作的进程数，这里使用了文档建议的值
# workers = 8
PROJECT_PROFILE = os.environ.get('PROJECT_PROFILE', 'local')
_worker_count = psutil.cpu_count(logical=False) * 2 + 1 if PROJECT_PROFILE == "prod" else 4
workers = _worker_count

# 默认值是：1000 该参数的含义是：每个工作线程同时存在的连接数，该参数仅在 Eventlet 和 Gevent 两种工作模式下有效
worker_connections = 1000

# 数据库连接数 mysql_max_connections = workers*threads*2
# 已知当前数据库最大连接数=6000
# show variables like '%connect%';
# max_connections，最大连接数。
mysql_max_connections = 6000
threads = int(int((mysql_max_connections - 40) / 2) / _worker_count)

# 访问超时时间
timeout = 60

# 接收到restart信号后，worker可以在graceful_timeout时间内，继续处理完当前requests。
graceful_timeout = 60

# server端保持连接时间。
keepalive = 30

max_requests = 2000  # 有内存泄露时使用此选项重启work
max_requests_jitter = 100  # 重启work的抖动幅度，一般设置为max_requests的5%

# 逗号分隔的Python执行路径，可以加上参数，这里只有一个路径，-u表示使用无缓冲的二进制终端输出流
# pythonpath = '/usr/bin/python3 -u'
# 日志文件格式
# access_log_format = '%(t)s %(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(L)s"'

today = datetime.now().strftime("%Y%m%d")
accesslog = access_logfile = os.path.join(LOG_ROOT, f'gnc_access_{today}.log')
errorlog = error_logfile = os.path.join(LOG_ROOT, f'gnc_error_{today}.log')

#!/bin/bash

# 容器内热加载启动脚本
# 使用方法：在容器内运行 ./hot_reload.sh

echo "停止 supervisord 服务..."


echo "设置开发环境变量..."
export DEBUG=True
supervisorctl restart main
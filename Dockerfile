FROM python:3.11

ENV DOCKER_HOME=/code/
ENV PROJECT_PROFILE=staging
ENV TZ=Asia/Shanghai
WORKDIR $DOCKER_HOME

# 先安装所有包，不复制配置文件
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing --no-install-recommends \
    supervisor tzdata \
    build-essential pkg-config default-libmysqlclient-dev \
    libxml2-dev libxslt1-dev zlib1g-dev \
    nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY ./ $DOCKER_HOME

# 安装 Python 依赖
RUN pip install -r $DOCKER_HOME/requirements.txt

# 安装完成后再覆盖配置文件
COPY ./builds/supervisord/supervisord.conf /etc/supervisord.conf
COPY ./builds/supervisord/super_main.ini /etc/supervisord.d/super_main.ini
COPY ./builds/nginx/nginx.conf /etc/nginx/nginx.conf

# 清理编译依赖
RUN apt-get remove -y build-essential pkg-config && \
    apt-get autoremove -y && \
    apt-get clean

EXPOSE 8000
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.conf"]
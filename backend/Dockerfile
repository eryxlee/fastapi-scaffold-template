FROM python:3.12.3-alpine3.19

# 字符集变量
ENV LANG='zh_CN.UTF-8' LANGUAGE='zh_CN:zh' LC_ALL='zh_CN.UTF-8'

# 时区变量
ENV TIME_ZONE=Asia/Shanghai TZ=Asia/Shanghai

# 工作目录
WORKDIR /code/

# 换源更新，安装工具包，设置市区。阿里云源：mirrors.aliyun.com
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache curl jq ttf-dejavu fontconfig tzdata && \
    mkdir -p /etc/zoneinfo/Asia/ && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/zoneinfo/Asia/Shanghai && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo Asia/Shanghai > /etc/timezone && \
    apk del tzdata && \
    rm -rf /tmp/* /var/cache/apk/*

# 安装 Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false && \
    poetry config repositories.tuna https://mirrors.aliyun.com/pypi/simple/

# 拷贝 poetry 文件
COPY ./pyproject.toml ./poetry.lock* /code/

# 安装python三方包
ARG INSTALL_DEV=false
RUN sh -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/code PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY ./log_conf.yaml ./manage.py ./.env* /code/

COPY ./static/ /code/static/

COPY ./app/ /code/app/

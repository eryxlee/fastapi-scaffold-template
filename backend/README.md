## Docker 开发环境配置
### 启动Python Docker
```shell
docker run -it --rm -p8080:8080 -v ./backend:/code python:3.12.3-alpine3.19 /bin/sh
```
## 安装必要的二进制包（Pillow 待确认）
```shell
apk add --virtual build-deps gcc python3-dev musl-dev
apk add jpeg-dev zlib-dev libjpeg
```
### 安装配置poetry
```shell
pip install poetry
```
按照已有poetry配置安装三方包：
```shell
poetry install --no-root
```
如果不想用现有的poetry配置，可以删掉两个poetry文件，按如下配置：
```shell
poetry source add --priority=primary mirrors https://pypi.tuna.tsinghua.edu.cn/simple/
poetry add fastapi uvicorn[standard] pydantic[email] pydantic_settings pydantic-extra-types phonenumbers aiomysql sqlmodel bcrypt python-jose redis-om fastapi-cache2 Pillow
poetry add httpx pytest pytest_asyncio pytest-timeout pytest-cov --group dev
```

### 运行程序
```
poetry shell
uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8080 --env-file=.env
pytest
pytest --cov=app --cov-branch
```
注意：因在docker中运行，数据库等链接信息不要使用127.0.0.1/localhost等方式。

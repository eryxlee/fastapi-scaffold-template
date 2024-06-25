# -*- coding: utf-8 -*-

from typing import Annotated, Any, Literal, Optional

from pydantic import (
    AnyHttpUrl,
    AnyUrl,
    BeforeValidator,
    MariaDBDsn,
    PostgresDsn,
    RedisDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class AppConfigSettings(BaseSettings):
    """应用配置 采用pydantic写法, 使用项目根目录下的.env文件来维护项目配置。.env 文件可以按照环境不同进行划分，
    分为.env、.env.test、.env.prod等, 在启动的时候加载不同的配置文件。

    配置项定义方法如下：
    app_name: str = Field(..., env="APP_NAME")  每个配置项都有一个默认值和一个与之关联的环境变量名。
        Field 对象用于指定配置项的默认值和环境变量名。... 表示该配置项是必需的，没有默认值。
    """

    APP_ENV: Literal["dev", "test", "prod"] = "dev"

    # 应用配置信息
    APP_NAME: str = "My FastAPI App"
    APP_VERSION: str = "0.0.1"
    APP_DESCRIPTION: Optional[str] = None
    DEBUG: bool = False
    BASE_URL: AnyHttpUrl = "http://127.0.0.1:8080"
    API_PREFIX: str = "/api"

    # 服务器配置信息
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    OPENAPI_URL: Optional[str] = (None,)  # 属性值设置为 None 时，表示不开启
    DOCS_URL: Optional[str] = (None,)  # 属性值设置为 None 时，表示不开启
    REDOC_URL: Optional[str] = None  # 属性值设置为 None 时，表示不开启
    CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    # cookie 配置信息
    COOKIE_KEY: str = "sessionId"  # key name
    COOKIE_MAX_AGE: int = 24 * 60 * 60  # 有效时间
    COOKIE_NOT_CHECK: list[str] = [
        "/api/user/login",
        "/api/user/signup",
    ]  # 不校验 Cookie

    # JWT 配置信息
    JWT_SECRET_KEY: str = "75e39662418f7f77877ccacad6486680a1351d1e81cc1876ff9f5493cb8fb7a6"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRED: int = 60
    JWT_ISS: str = ""
    JWT_NO_CHECK_URIS: list[str] = [
        "/",
        "/apidoc",
        "/openapi.json",
        "/api/user/login",
        "/favicon.ico",
    ]

    # 数据库配置
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_DATABASE: str = "test"
    DB_QUERY_STR: str = "charset=utf8mb4"
    DB_POOL_SIZE: int = 10
    DB_POOL_OVERFLOW: int = 40
    DB_ENABLE_ECHO: bool = True

    @computed_field
    @property
    def POSTGRES_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_DATABASE,
            query=self.DB_QUERY_STR,
        )

    @computed_field
    @property
    def MARIADB_DATABASE_URI(self) -> MariaDBDsn:
        return MultiHostUrl.build(
            scheme="mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_DATABASE,
            query=self.DB_QUERY_STR,
        )

    @computed_field
    @property
    def AIO_MARIADB_DATABASE_URI(self) -> MariaDBDsn:
        return MultiHostUrl.build(
            scheme="mysql+aiomysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_DATABASE,
            query=self.DB_QUERY_STR,
        )

    # redis配置
    REDIS_DSN: RedisDsn = "redis://127.0.0.1:6379/0"
    # redis settings without username -> redis://:123456@localhost:6379/0
    # aioredis settings -> aioredis://[[username]:[password]]@localhost:6379/0
    REDIS_EXPIRE: int = 24 * 60 * 60  # Redis 过期时长
    REDIS_PREFIX: str = "redis-om"  # Redis 全局前缀

    # celery
    CELERY_BROKER: str = "redis://127.0.0.1:6379/8"
    CELERY_BACKEND: str = "redis://127.0.0.1:6379/8"

    # email
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self):
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.APP_NAME
        return self

    @computed_field
    @property
    def EMAILS_ENABLED(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # 定义环境变量文件读取方式
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8"  # 指定环境变量文件的编码
        # env_file = ".env"
        # case_sensitive = True
        # env_prefix = "my_"
    )


settings = AppConfigSettings()

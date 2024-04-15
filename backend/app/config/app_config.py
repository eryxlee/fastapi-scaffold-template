# -*- coding: utf-8 -*-
import secrets

from typing import Annotated, Any, Literal
from pydantic import Field, RedisDsn
from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)

class AppConfigSettings(BaseSettings):
    """应用配置
    采用pydantic写法, 使用项目根目录下的.env文件来维护项目配置。.env 文件可以按照环境不同进行划分，
    分为.env、.env.test、.env.prod等, 在启动的时候加载不同的配置文件。

    配置项定义方法如下：
    app_name: str = Field(..., env="APP_NAME")  每个配置项都有一个默认值和一个与之关联的环境变量名。
        Field 对象用于指定配置项的默认值和环境变量名。... 表示该配置项是必需的，没有默认值。
    """
    APP_ENV: Literal["dev", "test", "prod"] = "dev"

    APP_NAME: str = "My FastAPI App"
    APP_VERSION: str
    APP_DESCRIPTION: str
    APP_DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8080
    DOMAIN: str = "localhost"

    @computed_field
    @property
    def server_host(self) -> str:
        if self.APP_ENV == "dev":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    API_PREFIX: str = "/api"
    SECRET: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    # 数据库配置
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str

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
        )

    # redis配置
    REDIS_DSN: RedisDsn = None

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
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # 内部类，定义环境变量文件读取方式
    class Config:
        env_file_encoding = "utf-8"  # 指定环境变量文件的编码
        # env_file = ".env"
        # case_sensitive = True
        # env_prefix = "my_"

settings = AppConfigSettings()
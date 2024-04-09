# -*- coding: utf-8 -*-

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings


class AppConfigSettings(BaseSettings):
    """应用配置
    采用pydantic写法, 结合项目根目录下的.env文件共同维护项目配置。.env 文件可以按照环境不同，
    分为.env、.env.test、.env.prod等, 在启动的时候加载不同的配置文件。

    配置项定义方法如下：
    app_name: str = Field(..., env="APP_NAME")  每个配置项都有一个默认值和一个与之关联的环境变量名。
        Field 对象用于指定配置项的默认值和环境变量名。... 表示该配置项是必需的，没有默认值。
    """
    app_env: str = ""
    app_name: str = "My FastAPI App"
    app_version: str
    app_description: str
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8080

    # 数据库配置
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_database: str

    # redis配置
    redis_dsn: RedisDsn = None

    # 内部类，定义环境变量文件读取方式
    class Config:
        env_file_encoding = "utf-8"  # 指定环境变量文件的编码
        # env_file = ".env"
        # case_sensitive = True
        # env_prefix = "my_"
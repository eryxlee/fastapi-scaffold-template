# -*- coding: utf-8 -*-

import os
import logging
from dotenv import load_dotenv
from functools import lru_cache

from app.config.app_config import AppConfigSettings

logger = logging.getLogger(__name__)

@lru_cache
def get_app_config(env_file: str=None) -> AppConfigSettings:
    """获取项目配置, 添加缓存防止多次重复读取"""

    # 尝试读取环境变量，以支持用户使用类似 APP_ENV="test" uvicorn app.main:app这种方式运行
    run_env = os.environ.get("APP_ENV", "")
    app_name = os.environ.get("APP_NAME", "")

    # 如果 APP_NAME 未设置，说明 uvicorn 未加载配置文件，需要加载
    if app_name == "":
        # 默认加载.env，如是其他环境，则加载 .env.test（测试） .env.prod（正式）
        env_file = ".env" if run_env == "" else f".env.{run_env}"
        load_config_file(env_file)

    # 实例化配置模型
    return AppConfigSettings()

def load_config_file(env_file: str=None):
    """从配置文件中加载到环境变量
    """
    # 从.env文件加载配置信息
    load_dotenv(env_file)

# -*- coding: utf-8 -*-

import click
import uvicorn
from dotenv import load_dotenv


@click.group()
@click.version_option(version="0.0.1")
def cli():
    r"""命令行管理界面.

    本项目几种启动案例：\n
    # 使用默认设置启动。环境变量.env, 日志配置log_conf.yaml \n python manage.py start \n

    # 使用.env.test作为配置文件 \n python manage.py start --env-file=.env.test \n

    # 使用.env.test作为配置文件, log_conf.yaml作为日志配置文件 \n python manage.py start --env-
    file=.env.test --log-config=log_conf.yaml \n

    # uvicorn 直接启动，使用.env配置, 没有加载log配置 \n uvicorn app.main:app \n

    # uvicorn 启动，使用.env.test配置, 没有加载log配置 \n uvicorn app.main:app --env-file=.env.test
    \n
    """


@cli.command("start")
@click.option("--env-file", default=".env", help="Project settings file.")
@click.option("--log-config", default="log_conf.yaml", help="Project logging settings file.")
def start(env_file, log_config):
    """启动项目."""
    load_dotenv(env_file)

    from app.config import settings
    from app.main import app

    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_config=log_config)


@cli.command("init-data")
@click.option("--env-file", default=".env", help="Project settings file.")
def init_data(env_file):
    """项目数据库初始化."""
    load_dotenv(env_file)

    import asyncio

    from app.models.init_data import init_data

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_data())


if __name__ == "__main__":
    cli()

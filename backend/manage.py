# -*- coding: utf-8 -*-

import click
import uvicorn

from dotenv import load_dotenv


@click.group()
@click.version_option(version='0.0.1')
def cli():
    """命令行管理界面

    本项目几种启动案例：\n
    # 使用默认设置启动，默认使用.env作为配置文件, log_conf.yaml作为日志文件 \n
    python manage.py start \n

    # 使用.env.test作为配置文件 \n
    python manage.py start --env-file=.env.test \n

    # 使用.env.test作为配置文件, log_conf.yaml作为日志配置文件 \n
    python manage.py start --env-file=.env.test --log-config=log_conf.yaml \n

    # uvicorn 直接启动，使用.env配置, 没有加载log配置 \n
    uvicorn app.main:app \n

    # uvicorn 启动，使用.env.test配置, 没有加载log配置 \n
    uvicorn app.main:app --env-file=.env.test \n
    """


@cli.command('start')
@click.option('--env-file', default=".env", help='Project settings file.')
@click.option('--log-config', default="log_conf.yaml", help='Project logging settings file.')
def start(env_file, log_config):
    load_dotenv(env_file)

    from app.config import settings
    from app.main import app

    uvicorn.run(
        app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_config=log_config
    )


if __name__ == '__main__':
    cli()

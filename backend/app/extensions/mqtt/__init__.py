# -*- coding: utf-8 -*-

import random

from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion


class MQTTClient:
    """MQTT客户端."""

    def __init__(self, broker, port):
        self.broker = broker
        self.port = port
        self.client_id = f"python-mqtt-{random.randint(0, 1000)}"  # noqa: S311
        self.client = None

    def connect(self):
        """建立MQTT连接."""

        def on_connect(client, userdata, flags, rc):
            # flags是一个包含代理回复的标志的字典；
            # rc的值决定了连接成功或者不成功（0为成功）
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        self.client = mqtt_client.Client(
            callback_api_version=CallbackAPIVersion.VERSION2, client_id=self.client_id
        )  # 实例化对象
        # self.client.on_connect = on_connect	# 设定回调函数，当Broker响应连接时，执行给定的函数
        self.client.connect(self.broker, self.port)  # 连接

    def publish(self, topic, message):
        """发送MQTT消息."""
        result = self.client.publish(topic, message)
        status = result[0]  # 解析响应内容
        if status == 0:  # 发送成功
            print(f"Send `{message}` to topic `{topic}`")
        else:  # 发送失败
            print(f"Failed to send message to topic {topic}")

    def start(self):
        """客户端启动."""
        self.client.loop_start()

    def stop(self):
        """客户端关闭."""
        self.client.loop_stop()

    def disconnect(self):
        """关闭MQTT连接."""
        self.client.disconnect()

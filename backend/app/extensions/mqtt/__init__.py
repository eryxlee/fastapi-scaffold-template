# -*- coding: utf-8 -*-

import random

from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt import client as mqtt_client


class MQTTClient(object):
    def __init__(self, broker, port):
        self.broker = broker
        self.port = port
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.client = None

    def connect(self):
        def on_connect(client, userdata, flags, rc):
        # flags是一个包含代理回复的标志的字典；
        # rc的值决定了连接成功或者不成功（0为成功）
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        self.client = mqtt_client.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=self.client_id)	# 实例化对象
        # self.client.on_connect = on_connect	# 设定回调函数，当Broker响应连接时，就会执行给定的函数
        self.client.connect(self.broker, self.port)	# 连接

    def publish(self, topic, message):
        result = self.client.publish(topic, message)
        status = result[0]	# 解析响应内容
        if status == 0:	# 发送成功
            print(f"Send `{message}` to topic `{topic}`")
        else:	# 发送失败
            print(f"Failed to send message to topic {topic}")

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def disconnect(self):
        self.client.disconnect()

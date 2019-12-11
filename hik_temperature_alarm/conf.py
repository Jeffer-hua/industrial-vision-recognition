import os

MQ_SETTING = {
    "host": "localhost",
    "username": "admin",  # mq用户名
    "password": "admin",  # mq密码
    "port": 5672,
    "queue_name": {
        "v_temperature": "vision_temperature"
    }
}
PTZ_SLEEP_TIME = 30
TEMPERATURE_NOW_RULE = 5
ICV_INSTALL_PATH = "./"

MODE_PATH_DICT = {
    "temperature": {
        "hk_sdk": os.path.join(ICV_INSTALL_PATH, "model/hk_infraed"),
    }
}

CAMERA_NAME = "admin"
CAMERA_PWD = "admin123"

CLIENT_IP = "0.0.0.0"
CLIENT_PORT = "10002"

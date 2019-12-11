# !/usr/bin/python3
# -*- coding:utf-8 -*-
# @time : 2019.10.26
# @IDE : pycharm
# @auto : jeff_hua
# @github : https://github.com/Jeffer-hua

import subprocess
import shutil
import datetime
import pika
import time
from utils.worker_producer import DataHandler
from conf import *
from utils.pid_function import kill_child_processes
import os


class DetectionHandler(object):
    def __init__(self, mq_param, queue_name):
        '''
        面板识别数据queue handler定义
        '''
        self.mq_param = mq_param
        self.queue_name = queue_name
        self.channel, self.connection = self.init_channel()
        self.data_mq_temperature = DataHandler(MQ_SETTING, MQ_SETTING["queue_name"]["d_temperature"])

    def init_channel(self):
        is_connection = True
        while is_connection:
            try:
                user_pwd = pika.PlainCredentials(self.mq_param['username'], self.mq_param['password'])
                # 创建连接对象
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.mq_param['host'], port=self.mq_param['port'], virtual_host='/',
                                              credentials=user_pwd,
                                              heartbeat_interval=0))
                # 创建频道对象
                channel = connection.channel()
                # 切换到指定的队列,如果不存在则创建
                channel.queue_declare(queue=self.queue_name, durable=True, arguments={'x-max-length': 50})
                channel.basic_consume(
                    queue=self.queue_name,
                    # 回调函数
                    consumer_callback=self.callback,
                    no_ack=False
                )
                is_connection = False
                return channel, connection
            except Exception as e:
                time.sleep(1)

    def detection(self):
        """消费，接收消息..."""
        disconnected = True
        while disconnected:
            try:
                disconnected = False
                self.channel.start_consuming()  # blocking call
            except pika.exceptions.ConnectionClosed:  # when connection is lost, e.g. rabbitmq not running
                disconnected = True
                time.sleep(1)  # reconnect timer
                self.channel, self.connection = self.init_channel()

    # @detection_timer
    def callback(self, ch, method, properties, body):
        try:
            # body : RabbitMQ消息队列中传递的消息
            # 保证响应
            ch.basic_ack(delivery_tag=method.delivery_tag)
            data = eval(body)
            if data:
                is_all = True
                img_save_dir = os.path.join(ICV_RESULT_IMG_PATH, IMG_NAME_DICT["temperature_dir_name"],
                                            data["camera_id"])
                temperature_dir = os.path.join(img_save_dir, "infraed_temperature")
                origin_dir = os.path.join(img_save_dir, "infraed_origin")
                if not os.path.exists(temperature_dir):
                    os.makedirs(temperature_dir)
                if not os.path.exists(origin_dir):
                    os.makedirs(origin_dir)

                load_sdk_data_path = os.path.join(ICV_INSTALL_PATH, "vision/temperature_detection/infraed_now.py")
                previous_working_directory = os.getcwd()
                out = subprocess.Popen(
                    "/usr/bin/python3 {} {} {} {} {} {}".format(load_sdk_data_path, data["camera_ip"],
                                                                MODE_PATH_DICT["temperature"]["hk_sdk"], CAMERA_NAME,
                                                                CAMERA_PWD,
                                                                img_save_dir),
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=True)
                os.chdir(previous_working_directory)

                start_time = datetime.datetime.now()
                preset_no_list = []
                preset_no_set = ()
                while is_all:
                    try:
                        # Get Hk SDK output
                        std_out = out.stdout.readline().decode('utf-8')
                        if std_out.find('CPP CurrTemperature:') == 0:
                            detection_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            std_out = std_out[len("CPP CurrTemperature:"):-1]
                            height_point_x, height_point_y, ptz_info_pan, ptz_info_tilt, ptz_info_zoom, preset_no, rule_temperature, \
                            curr_temperature = std_out.split('_')
                            curr_temperature = curr_temperature.replace(".jpg", "")
                            result_name = "{}.jpg".format(str(time.time()).replace(".", ""))
                            shutil.move(os.path.join(temperature_dir, std_out),
                                        os.path.join(temperature_dir, result_name))
                            shutil.move(os.path.join(origin_dir, std_out), os.path.join(origin_dir, result_name))
                            msg_key = "temperature_ok"
                            post_data_rabbitmq = {
                                "post_data": {"camera_id": data["camera_id"],
                                              "temperature_result_path": os.path.join(temperature_dir, result_name),
                                              "origin_result_path": os.path.join(origin_dir, result_name),
                                              "preset_no": preset_no,
                                              "height_point_x": height_point_x,
                                              "height_point_y": height_point_y,
                                              "temp_threshold": TEMPERATURE_NOW_RULE,
                                              "current_temp": curr_temperature,
                                              "detection_time": detection_time,
                                              "msg_key": msg_key},
                                "post_type": "temperature"
                            }
                            # print(preset_no)
                            self.data_mq_temperature.upload_img(post_data_rabbitmq)
                            preset_no_list.append(preset_no)
                            # 判断是否巡航结束业务逻辑
                            preset_no_set = set(preset_no_list)
                        # 超时时间判断巡航模式结束业务逻辑
                        now_time = datetime.datetime.now()
                        if (now_time - start_time).seconds > int(data["preset_no_number"]) * PTZ_SLEEP_TIME or len(
                                preset_no_set) == int(data["preset_no_number"]):
                            is_all = False
                            kill_child_processes(out.pid)
                            out.kill()
                    except Exception as e:
                        pass
                        # self.log_handle.error("hk temperature now failed preset_no error {}".format(e))
        except Exception as e:
            pass
            # self.log_handle.error("Check data error {}".format(e), exc_info=True)


if __name__ == '__main__':
    detection_mq = DetectionHandler(MQ_SETTING, MQ_SETTING["queue_name"]["v_temperature"])
    detection_mq.detection()

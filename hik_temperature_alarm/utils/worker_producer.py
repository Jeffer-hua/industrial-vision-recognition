# !/usr/bin/python3
# -*- coding:utf-8 -*-
# @time : 2019.05.06
# @IDE : pycharm
# @auto : jeff_hua
# @github : https://github.com/Jeffer-hua

import pika
import time


class DataHandler(object):
    def __init__(self, mq_param, queue_name, log_handle=None):
        '''
        Init rabbitmq direct(订阅发布模式生产者初始化)
        :param mq_param: rabbitmq param(定义参数)
        :param queue_name: rabbitmq queue(队列名称)
        :param log_handle: logging(日志)
        '''
        self.mq_param = mq_param
        self.log_handle = log_handle
        self.queue_name = queue_name
        self.channel, self.connection = self.init_channel()

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
                is_connection = False
                return channel, connection
            except Exception as e:
                # self.log_handle.error('Rabbitmq init error --> {}'.format(e), exc_info=True)
                time.sleep(1)
                # self.log_handle.info('Rabbitmq re-init')

    def keep_alive(self):
        # on time seed heartbeat
        try:
            self.connection.process_data_events()
        except Exception as e:
            # self.log_handle.error('Rabbitmq connect error --> {}'.format(e), exc_info=True)
            time.sleep(1)
            # self.log_handle.info('Rabbitmq re-connect')
            self.channel, self.connection = self.init_channel()

    def upload_img(self, data):
        '''
        multiprocessing upload image
        :param data: upload data
        :return:
        '''
        try:
            self.channel.basic_publish(exchange='',
                                       routing_key=self.queue_name,
                                       body=str(data),
                                       properties=pika.BasicProperties(delivery_mode=2,  # make message persistent
                                                                       ))
        except Exception as e:
            # self.log_handle.error('upload_img error --> {}'.format(e), exc_info=True)
            print(e)

    def __del__(self):
        self.connection.close()

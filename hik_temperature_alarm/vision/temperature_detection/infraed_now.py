# !/usr/bin/python3
# -*- coding:utf-8 -*-
# @time : 2019.12.09
# @IDE : pycharm
# @auto : jeff_hua
# @github : https://github.com/Jeffer-hua
import time
import ctypes
import os
import sys


def get_temperature(camera_ip, sdk_path, camera_name, camera_pwd, img_save_dir, camera_port=8000):
    infraed_so = os.path.join(sdk_path, "getpsdata_now.so")
    os.chdir(sdk_path)
    h_dll = ctypes.cdll.LoadLibrary(infraed_so)
    # hk sdk input data must be bytes
    camera_ip = bytes(camera_ip, 'ascii')
    camera_name = bytes(camera_name, 'ascii')
    camera_pwd = bytes(camera_pwd, 'ascii')
    img_save_dir = bytes(img_save_dir, 'ascii')
    # FaceDetectAndContrast
    '''
    param camera_ip:hk infraed camera
    param port: default 8000
    param user_name:user_name
    param user_pwd:user_pwd
    '''
    h_dll.InfraedTemperature(camera_ip, camera_port, camera_name, camera_pwd, img_save_dir)
    while True:
        # keep alive
        time.sleep(200)


if __name__ == '__main__':
    camera_ip = sys.argv[1]
    sdk_path = sys.argv[2]
    camera_name = sys.argv[3]
    camera_pwd = sys.argv[4]
    img_save_dir = sys.argv[5]
    get_temperature(camera_ip, sdk_path, camera_name, camera_pwd, img_save_dir)

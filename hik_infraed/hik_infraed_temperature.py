# -*- coding:utf-8 -*-
import time
import ctypes
import os
import sys


def infraed_temperature(camera_ip, sdk_path, camera_name, camera_pwd, camera_port=8000):
    face_snap_so = os.path.join(sdk_path, "getpsdata_infraed.so")
    os.chdir(sdk_path)
    h_dll = ctypes.cdll.LoadLibrary(face_snap_so)
    # hk sdk input data must be bytes
    camera_ip = bytes(camera_ip, 'ascii')
    camera_name = bytes(camera_name, 'ascii')
    camera_pwd = bytes(camera_pwd, 'ascii')
    # FaceDetectAndContrast
    '''
    param camera_ip:hk infraed camera
    param port: default 8000
    param user_name:user_name
    param user_pwd:user_pwd
    '''
    h_dll.InfraedTemperature(camera_ip, camera_port, camera_name, camera_pwd)
    while True:
        # keep alive
        time.sleep(200)

if __name__ == '__main__':
    camera_ip = sys.argv[1]
    sdk_path = sys.argv[2]
    camera_name = sys.argv[3]
    camera_pwd = sys.argv[4]
    infraed_temperature(camera_ip, sdk_path, camera_name, camera_pwd)

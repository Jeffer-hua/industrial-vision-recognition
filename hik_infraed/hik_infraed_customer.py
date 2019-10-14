import multiprocessing as mp
import time
import numpy as np
import subprocess
import shutil
import os


def customer_infraed(queue, CAMERA_NAME, CAMERA_PWD, camera_ip, camera_id, num_camera=1):
    load_sdk_data_path = os.path.join("./hik_infraed_temperature.py")
    previous_working_directory = os.getcwd()
    out = subprocess.Popen(
        "python3 {} {} {} {} {}".format(load_sdk_data_path, camera_ip, "./hk_infraed", CAMERA_NAME,
                                        CAMERA_PWD),
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True)
    os.chdir(previous_working_directory)
    # Init RabbitMQ to put image
    while True:
        # Get Hk SDK output
        std_out = out.stdout.readline().decode('utf-8')
        if std_out.find('CPP match infrared_info:') == 0:
            std_out = std_out[len("CPP match infrared_info:"):-1]
            chTime_back, max_temperature, aver_temperature, min_temperature = std_out.split('_')
            print("最大温度:", max_temperature, "平均温度:", aver_temperature, "最小温度:", min_temperature)


def run():
    process_icv = []
    camera_ip_list = ["192.168.1.66"]
    camera_id_list = ["50002"]
    camera_type_list = ["rtsp"]
    if camera_ip_list:
        queue_face_list = [mp.Queue(maxsize=2) for _ in camera_ip_list]

        for queue, camera_ip, camera_id, camera_type in zip(queue_face_list, camera_ip_list, camera_id_list,
                                                            camera_type_list):
            process_icv.append(
                mp.Process(target=customer_face,
                           args=(queue, "admin", "admin123", camera_ip, camera_id)))

    [process.start() for process in process_icv]
    [process.join() for process in process_icv]


if __name__ == '__main__':
    run()

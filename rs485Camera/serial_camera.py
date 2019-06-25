import serial
import time
import cv2
import logging
import numpy as np
import argparse

'''
A serial camera protocol to get image
 
Environment : Ubuntu18.04+python3.6+

Access protocol : RS485

Run: python3 serial_camera.py --com ttyUSB0 --port 0 --img test.jpg

Development : jeffa
'''

logger_script = logging.getLogger(__name__)
logger_script.setLevel(level=logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# FileHandler
file_handler = logging.FileHandler("./serial_com.log")
file_handler.setFormatter(formatter)
logger_script.addHandler(file_handler)


class SerialCamera(object):
    def __init__(self, com_serial):
        try:
            self.port = serial.Serial(com_serial, baudrate=38400, bytesize=serial.EIGHTBITS, timeout=2)
        except Exception as e:
            logger_script.error('serial open {}'.format(e), exc_info=True)

    def __del__(self):
        self.port.close()

    def reset(self, no):
        '''
        Reset serial_com
        :param no: port
        :return: True or False
        '''
        cmd = [0x56, no, 0x26, 0x00]
        correct_response = "76 %02x 26 00 " % no
        self.port.write(cmd)
        response = self.port.read(4)
        res = ''.join(['%02x ' % b for b in response])  # Attention：should add one more space
        if (res == correct_response):
            return True
        else:
            logger_script.error('serial camera error reset', exc_info=True)
            return False

    def modify_port(self, no1, no2):
        '''
        Modify serial_com port
        :param no1: new port
        :param no2: old port
        :return: True or False
        '''
        cmd = [0x56, no2, 0x31, 0x05, 0x04, 0x01, 0x00, 0x06, no1]
        correct_response = "76 %02x 31 00 00 " % no2
        self.port.write(cmd)
        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # Attention：should add one more space
        if (res == correct_response):
            # After modifying the port,new port reset is required
            return self.reset(no2)
        else:
            logger_script.error('serial camera error modify!', exc_info=True)
            return False

    def set_image_compression(self, no, XX=0x36):
        '''
        Set image compression
        :param no: port
        :param XX: ratio:00~FF,default:0x36
        :return: True or False
        '''
        cmd = [0x56, no, 0x31, 0x05, 0x01, 0x01, 0x12, 0x04, XX]
        correct_response = "76 %02x 31 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)
        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # Attention：should add one more space
        if (res == correct_response):
            return True
        else:
            logger_script.error('serial camera error compression!', exc_info=True)
            return False

    def set_image_pixel(self, no, res=0x00):
        '''
        Set image pixel
        :param no: port
        :param res: res = 0x00 640x480，11 320x240， 22 160x120
        :return: True or False
        '''
        cmd = [0x56, no, 0x31, 0x05, 0x04, 0x01, 0x00, 0x19, res]
        correct_response = "76 %02x 31 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)
        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # Attention：should add one more space
        if (res == correct_response):
            return True
        else:
            logger_script.error('serial camera error set pixel!', exc_info=True)
            return False

    def clear_buff(self, no):
        '''
        Clear serial_com return data
        :param no: port
        :return: True or False
        '''
        cmd = [0x56, no, 0x36, 0x01, 0x02]
        correct_response = "76 %02x 36 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)
        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # Attention：should add one more space
        if (res == correct_response):
            return True
        else:
            logger_script.error('serial camera error clear_buff!', exc_info=True)
            return False

    def get_image_command(self, no):
        '''
        A command of get image
        :param no: port
        :return: True or False
        '''
        cmd = [0x56, no, 0x36, 0x01, 0x00]
        correct_response = "76 %02x 36 00 00 " % no  # eg: 76 00 31 00 00
        self.port.write(cmd)
        response = self.port.read(5)
        res = ''.join(['%02x ' % b for b in response])  # Attention：should add one more space
        if (res == correct_response):
            return True
        else:
            logger_script.error('serial camera error command!', exc_info=True)
            return False

    def get_image_len(self, no):
        '''
        Get serial_com image len
        :param no: port
        :return: image len
        '''
        cmd = [0x56, no, 0x34, 0x01, 0x00]
        correct_response = "76 %02x 34 00 04 00 00 " % no  # eg: 76 02 34 00 04 00 00
        self.port.write(cmd)
        response = self.port.read(9)
        res = ''.join(['%02x ' % b for b in response[0:7]])  # Attention：should add one more space
        if (res == correct_response):
            return response[7:9]
        else:
            logger_script.error('serial camera error get_image_len!', exc_info=True)
            return []

    def get_image(self, no, img_len, filename):
        '''
        Get image
        :param no: port
        :param img_len: the length of image
        :param filename: image path
        :return: True or False
        '''
        try:
            byteLen = int.from_bytes(img_len, byteorder='big', signed=False)
            i, j = 0, 0
            cmd = [0x56, no, 0x32, 0x0c, 0x00, 0x0a, 0x00, 0x00, (i & 0xff00) >> 8, (i & 0x00ff), 0x00, 0x00,
                   (byteLen & 0xff00) >> 8, (byteLen & 0x00ff), 0x00, 0xff]
            self.port.write(cmd)
            time.sleep(15)  # The time is serial receives data,680 needs 15s+
            re = self.port.read(byteLen + 50)
            wf = open(filename, "wb")
            wf.write(re[5:-5])
            wf.close()
            image = cv2.imread(filename)
            if isinstance(image, np.ndarray):
                return True
            else:
                logger_script.error('serial camera error get_image!')
                return False
        except:
            logger_script.error('serial camera get_image_data broken')
            return False

    def update(self, no, filename):
        try:
            is_command = self.get_image_command(no)
            if is_command:
                image_len = self.get_image_len(no)
                return len(image_len) > 0 and self.get_image(no, image_len, filename) and self.clear_buff(no)
            else:
                return False
        except Exception as e:
            logger_script.info('||| Error serial get_image {}!'.format(e), exc_info=True)
            return False


def update(serial_com, port, img_save_path):
    '''
    get serial camera image
    :param serial_com: serial camera eg:ttyUSB0
    :param port: serial camera port 0
    :param img_save_path: output image path
    :return: ok or wrong
    '''
    # cv2.namedWindow("serial_camera", cv2.WINDOW_FREERATIO)
    # 注意串口不能连续关闭打开，会导致生成的图片丢帧
    sc = SerialCamera(serial_com)
    is_append = sc.update(int(port), img_save_path)
    if is_append:
        origin_img = cv2.imread(img_save_path)
        if isinstance(origin_img, np.ndarray):
            return "ok"
            # cv2.imshow("serial_camera", show_img)
            # cv2.waitKey(0)
    else:
        return "wrong"


def modify_port(serial_com, ori_port, new_port):
    '''
    modify serial camera port
    :param serial_com: serial camera eg:ttyUSB0
    :param ori_port: serial camera origin port
    :param new_port: serial camera new port
    :return: ok or wrong
    '''
    sc = SerialCamera(serial_com)
    is_modify = sc.modify_port(new_port, ori_port)
    if is_modify:
        return "ok"
    else:
        return "wrong"


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--com", "-c", help="serial_com")
    parser.add_argument("--port", "-p", help="serial_port")
    parser.add_argument("--img", "-i", help="img_save_path")

    args = parser.parse_args()
    if args.img_save_path:
        serial_com = args.com
        serial_port = args.port
        img_save_path = args.img
        update(serial_com, serial_port, img_save_path)
        print('||| Completed')
    else:
        print('||| Without query parameters, exit.')

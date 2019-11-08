import cv2
import numpy as np


def sub_image(image_minuend, image_subtrahend, add, mutl=1):
    '''
    Halcon : sub_image
    :param image_minuend: minuend image
    :param image_subtrahend: subtrahend image
    :param add: a param to enhance light of image
    :param mutl: the contrast of two large images after subtraction
    :return:
    '''
    dst = cv2.subtract(image_minuend, image_subtrahend)
    mask = np.zeros(dst.shape, dst.dtype)
    mask = np.full(mask.shape, int(add), dtype=np.uint8)
    img_sub = cv2.add(mask, dst)
    return img_sub

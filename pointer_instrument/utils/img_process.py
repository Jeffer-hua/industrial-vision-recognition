import cv2
import numpy as np


def img_sharpen(image):
    '''
    锐化
    '''
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)
    dst = cv2.filter2D(image, -1, kernel=kernel)
    return dst


def img_guass(image, kernel=(3, 3)):
    '''
    高斯模糊
    '''
    dst = cv2.GaussianBlur(image, kernel, 0)
    return dst


def gen_ring_region(image, x, y, radius_inner, radius_outer):
    '''
    获得圆形区域
    :param image:
    :param x:
    :param y:
    :param radius_inner:
    :param radius_outer:
    :return:
    '''
    circle1 = np.zeros(image.shape[:2], dtype="uint8")
    circle2 = np.zeros(image.shape[:2], dtype="uint8")
    c1 = cv2.circle(circle1, (x, y), radius_inner, 255, -1)
    c2 = cv2.circle(circle2, (x, y), radius_outer, 255, -1)
    bitwise_xor = cv2.bitwise_xor(c1, c2)
    mask = cv2.bitwise_and(image, image, mask=bitwise_xor)
    return mask


def rm_char(img, img_tmp, th=100):
    # 根据模板图去除指针上的刻度信息等，对一些较短指针作用较大
    guass = img_guass(img)
    guass_tmp = img_guass(img_tmp)
    sharpen = img_sharpen(guass)
    sharpen_tmp = img_sharpen(guass_tmp)
    ret, thresh = cv2.threshold(sharpen, th, 255, cv2.THRESH_OTSU)
    ret, thresh_tmp = cv2.threshold(sharpen_tmp, th, 255, cv2.THRESH_OTSU)
    idx = np.bitwise_and(thresh_tmp < th, thresh < th)
    thresh[idx] = 255
    return thresh


def orb_match(img, img_tmp, tmp_pts, img_ring_tmp):
    # ORB特征点匹配,透视变换模板图上的圆坐标
    rows, cols = img.shape[:2]
    detector = cv2.ORB_create()
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    kp1, desc1 = detector.detectAndCompute(img_tmp, None)
    kp2, desc2 = detector.detectAndCompute(img, None)
    raw_matches = matcher.knnMatch(desc1, desc2, 2)  # 2
    good = []
    for m, n in raw_matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)
    if len(good) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        pts = np.float32(tmp_pts).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        img_ring_tmp = cv2.warpPerspective(img_ring_tmp, M, (cols, rows))
        # matchesMask = mask.ravel().tolist()
        # draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
        #                    singlePointColor=(0, 0, 255),
        #                    matchesMask=matchesMask,
        #                    flags=2)  # draw only inliers
        # vis = cv2.drawMatches(img, kp1, img_tmp, kp2, good, None, **draw_params)
        # cv2.imwrite("vis.jpg", vis)
        return np.int32(dst).reshape(-1, 2), img_ring_tmp,True
    else:
        return None, None,False

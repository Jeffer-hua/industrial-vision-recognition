import cv2
from utils.circle_params import *
from utils.img_process import *
from conf import *
import time

'''
识别部分
'''


def move_img(img, col, row):
    H = np.float32([[1, 0, col], [0, 1, row]])
    rows, cols = img.shape[:2]
    dst = cv2.warpAffine(img, H, (cols, rows))
    cv2.imwrite("move.jpg", dst)


def show_result(img, x0, y0, radius_outer, radius_inner, cul_val, cul_degree):
    x_out, y_out = get_points_in_circle(x0, y0, radius_outer, cul_degree)
    cv2.circle(img, (int(x0), int(y0)), 5, (0, 0, 255), -1)
    cv2.circle(img, (int(x0), int(y0)), int(radius_outer), (0, 255, 0), 2)
    cv2.circle(img, (int(x0), int(y0)), int(radius_inner), (0, 255, 0), 2)
    put_strimg = "Values:%s" % (round(cul_val, 2))
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, put_strimg, (int(x0), int(y0)), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.line(img, (int(x0), int(y0)), (x_out, y_out), (0, 0, 255), 2)
    return img


def get_cul_values(thresh, ang_start, ang_end, points_range, x0, y0, radius_inner, radius_outer, min_degree=1):
    gray_mean = []
    range_degree = np.arange(ang_start, ang_end, min_degree)
    for deg in range_degree:
        sector = np.zeros(thresh.shape[:2], dtype="uint8")
        mask = cv2.ellipse(sector, (x0, y0), (radius_outer, radius_outer), deg, 0, min_degree, 255, -1)
        mask = cv2.ellipse(mask, (x0, y0), (radius_inner, radius_inner), deg, 0, min_degree, 0, -1)
        img_remain = cv2.bitwise_and(thresh, thresh, mask=mask)
        gray_mean.append(np.sum(img_remain) / np.sum(mask))
    gray_mean_val = np.array(gray_mean)
    liner_val = (points_range[1] - points_range[0]) / (ang_end - ang_start)
    cul_val = np.argmin(gray_mean_val) * min_degree * liner_val + points_range[0]
    cul_degree = range_degree[np.argmin(gray_mean_val) * min_degree]
    return cul_val, cul_degree


def pressure_detection(image, image_tmp, points_range, tmp_pts):
    # 灰度化
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_tmp = cv2.cvtColor(image_tmp, cv2.COLOR_BGR2GRAY)
    # 得到模板图中的参数以及模板图的mask区域
    print(tmp_pts)
    x0_tmp, y0_tmp, r_outer_tmp, r_inner_tmp = get_circle_param(tmp_pts[:3], tmp_pts[3:])
    img_ring_tmp = gen_ring_region(gray_tmp, x0_tmp, y0_tmp, r_outer_tmp, r_inner_tmp)
    # ORB特征匹配,对模板图的标志点和mask区域做映射变化
    warp_pts, img_ring_tmp, is_orb = orb_match(gray, gray_tmp, tmp_pts, img_ring_tmp)
    if is_orb:
        warp_pts = warp_pts.tolist()
        print(warp_pts)
        outer_pts, inner_pts = warp_pts[:3], warp_pts[3:]
        # 获得当前图片的mask区域
        x0, y0, radius_outer, radius_inner = get_circle_param(outer_pts, inner_pts)
        img_ring = gen_ring_region(gray, x0, y0, radius_inner, radius_outer)
        # 去除文字区域干扰
        thresh = rm_char(img_ring, img_ring_tmp, th=100)
        # 线性计算角度
        ang_start, ang_end = get_range_degree(x0, y0, outer_pts)
        cul_val, cul_degree = get_cul_values(thresh, ang_start, ang_end, points_range, x0, y0, radius_inner,
                                             radius_outer)
        # draw
        img = show_result(image, x0, y0, radius_outer, radius_inner, cul_val, cul_degree)
        print(cul_val, cul_degree)
        cv2.imwrite("points.jpg", img)


if __name__ == "__main__":
    image = cv2.imread(IMG_PATH)
    image_tmp = cv2.imread(TEMPLATE_IMG_PATH)
    pressure_detection(image, image_tmp, POINTS_RANGE, TMP_PTS)
    # move_img(image,50,35)

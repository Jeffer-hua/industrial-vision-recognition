import numpy as np
import math

'''
数学公式部分
'''


def fit_circle(pts):
    # 三点确定一个圆，确定的外圆轮廓
    x1, x2, x3 = pts[0][0], pts[1][0], pts[2][0]
    y1, y2, y3 = pts[0][1], pts[1][1], pts[2][1]
    a = x1 - x2
    b = y1 - y2
    c = x1 - x3
    d = y1 - y3
    e = ((x1 * x1 - x2 * x2) + (y1 * y1 - y2 * y2)) / 2.0
    f = ((x1 * x1 - x3 * x3) + (y1 * y1 - y3 * y3)) / 2.0
    det = b * c - a * d
    if (math.fabs(det) < 1e-5):
        return 0, 0, -1
    x0 = -(d * e - b * f) / det
    y0 = -(a * f - c * e) / det
    r = math.hypot(x1 - x0, y1 - y0)
    return round(x0), round(y0), round(r)


def get_points_in_circle(x, y, radius, degree):
    # 已知圆心半径和角度,求圆上一点
    x_out = x + radius * math.cos(degree * math.pi / 180)
    y_out = y + radius * math.sin(degree * math.pi / 180)
    return round(x_out), round(y_out)


def dist_2_pts(x1, y1, x2, y2):
    # 两点欧式距离
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def get_circle_param(outer_pts, inner_pts):
    # 拟合外圆,因为半径大误差会降低，获得内外圆参数
    x0, y0, radius_outer = fit_circle(outer_pts)
    radius_inner = 0  # 内圆半径通过列表取最大的轮廓最为半径
    for pts in inner_pts:
        x, y = pts[0], pts[1]
        r = round(dist_2_pts(x0, y0, x, y))
        if r > radius_inner:
            radius_inner = r
    return int(x0), int(y0), int(radius_outer), int(radius_inner)


def get_range_degree(x, y, outer_pts):
    # 获取圆环上测量开始角度和结束角度
    x1, y1 = outer_pts[0][0], outer_pts[0][1]
    x2, y2 = outer_pts[-1][0], outer_pts[-1][1]
    angle1 = math.atan2(y1 - y, x - x1) / math.pi * 180
    angle2 = math.atan2(y2 - y, x2 - x) / math.pi * 180
    return round(180 - angle1), round(360 + angle2)

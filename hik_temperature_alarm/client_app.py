#!/usr/bin/python3
# -*- coding:utf-8 -*-
from utils.worker_producer import DataHandler
from conf import *
from flask import Flask, request, jsonify

app = Flask(__name__)

vision_mq_temperature = DataHandler(MQ_SETTING, MQ_SETTING["queue_name"]["v_temperature"])


def icv_msgStringify(success, msg, status, data):
    return jsonify({
        "success": success,
        "message": msg,
        "status": status,
        "data": data,
    })


# 立即查看最新测温功能
@app.route('/temperature_now', methods=['POST'])
def temperature_now():
    try:
        data = request.json
        camera_info = {
            'camera_ip': data["camera_ip"],
            'camera_id': data["camera_id"],
            'preset_no_number': data["preset_no_number"],
        }
        vision_mq_temperature.upload_img(camera_info)
        return icv_msgStringify(True, 'Temperature now success', 200, '')
    except Exception as e:
        return icv_msgStringify(False, 'Temperature now failed : post data error', 400, "")


if __name__ == "__main__":
    app.run(host=CLIENT_IP, port=CLIENT_PORT, debug=True)

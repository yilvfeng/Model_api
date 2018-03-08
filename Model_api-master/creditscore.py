# -*- coding: utf-8 -*-
import json
import time
import sys
import pandas as pd
import math
import traceback
from flask import Flask, Blueprint
from flask import request
import logging
from settings import log_path, mark_path ,log_formatter ####配置文件
from logging import handlers, Formatter, getLogger
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (RandomTreesEmbedding, RandomForestClassifier,
                              GradientBoostingClassifier)
from sklearn.preprocessing import OneHotEncoder


reload(sys)
sys.setdefaultencoding('utf-8')

####配置模型目录


ios_clf1 = joblib.load('Model_file/Ios_lr_0.model')
ios_clf2 = joblib.load('Model_file/Ios_lr_15.model')
ios_clf3 = joblib.load('Model_file/Ios_lr_30.model')
android_clf1 = joblib.load('Model_file/Android_lr_0.model')
android_clf2 = joblib.load('Model_file/Android_lr_15.model')
android_clf3 = joblib.load('Model_file/Android_lr_30.model')

####配置变量名称
ios_columns = ["dev_login_cnt","yunfeng_historyloantimes","zdcy_score","cuishou_cnt","tongdun_cnt_apply_3m","tongdun_cnt_apply_7day","device_city_cnt",
                "channel_overduerate","contact_early_morning","user_isin_yq_30_contacts","yunfeng_currentoverduetimes","user_apply_hour","txl_apply_cnt",
				"yq_call_cnt","phone_yq_30_cnt","user_login_interval_60s","user_login_cnt"]


android_columns = ["dev_login_cnt","yunfeng_historyloantimes","tongdun_cnt_apply_3m","cuishou_cnt","zdcy_score","tongdun_cnt_apply_7day",
				"txl_call_rate","history_reject_cnt","user_login_cnt","is_android_7","yunfeng_currentoverduetimes","channel_overduerate",
				"dev_login_interval_60s_cnt","txl_reject_cnt","user_isin_yq_30_contacts","contact_early_morning"]



creditscoreApi = Blueprint('creditscroeApi', __name__)

log_path = log_path + "/creditscoreApi.log"
logger = getLogger('creditscore_model')
handler = handlers.RotatingFileHandler(log_path,maxBytes=100 * 1024 * 1024,backupCount=5)
formatter = Formatter(log_formatter)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(20)


def write_log(log_path, result):
    f = open(log_path,"a+")
    f.write(result+'\n')
    f.close()



@creditscoreApi.route("/model_api/creditscore/ios", methods=["POST"])
def get_result_ios():
    log_path_exe = mark_path + "/creditscore.log." + time.strftime("%Y-%m-%d", time.localtime())
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    resp = {"Model_name":"creditscore_ios","sUserId":[],"current_time": current_time,"msg": "ok", "code": 0, "input_data": [],"data_final": [], "result": 0}

    logger.info(
        'receive a  ios_creditscoreApi  request: {0}'.format(str(request)))
    try:
        ####获取数据

        input_data = request.form['input_data'].encode("utf-8")

        input_data = eval(input_data)

        ###解析数据
        get_data = pd.DataFrame(input_data, index=[0])
        ###数据处理

        #####选取入模型的指标
        data_final = get_data[ios_columns]

        #####加载模型预测

        result1 = int(round((ios_clf1.predict_proba(data_final)[:, 0] * 927.0), 0))
        result2 = int(round((ios_clf2.predict_proba(data_final)[:, 0] * 989.4), 0))
        result3 = int(round((ios_clf3.predict_proba(data_final)[:, 0] * 1000), 0))

        result = min(result1, result2, result3)

        #####结果保存
        resp['input_data'] = input_data
        resp['data_final'] = data_final.to_json(orient='records')
        resp['result'] = result
        resp['sUserId'] = get_data['sUserId'][0]
        write_log(log_path_exe,json.dumps(resp, ensure_ascii=False))

    except Exception, e:
        print "ERROR\n\n"
        resp['code'] = 1
        resp['msg'] = traceback.format_exc()
        logger.error(str(request) + resp['msg'])

    return json.dumps(resp, ensure_ascii=False)


######安卓API
@creditscoreApi.route("/model_api/creditscore/android", methods=["POST"])
def get_result_android():
    log_path_exe = mark_path + "/creditscore.log." + time.strftime("%Y-%m-%d", time.localtime())
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    resp = {"Model_name":"creditscore_android","sUserId":[],"current_time": current_time, "msg": "ok", "code": 0, "input_data": [], "data_final": [], "result": 0}

    logger.info(
        'receive a  android_creditscoreApi  request: {0}'.format(str(request)))
    try:
        ####获取数据

        input_data = request.form['input_data'].encode("utf-8")

        input_data = eval(input_data)

        ###解析数据
        get_data = pd.DataFrame(input_data, index = [0])

        ###数据处理
        if get_data['version_num'][0].split('.')[0] == '7':
            get_data['is_android_7'] = 1
        else:
            get_data['is_android_7'] = 0
        #####选取入模型的指标

        data_final = get_data[android_columns]


        #####加载模型预测
        result1 = int(round((android_clf1.predict_proba(data_final)[0, 0]) * 685.8, 0))
        result2 = int(round((android_clf2.predict_proba(data_final)[0, 0] * 933.7), 0))
        result3 = int(round((android_clf3.predict_proba(data_final)[0, 0] * 1000), 0))

        result = min(result1, result2, result3)

        resp['input_data'] = input_data
        resp['data_final'] = data_final.to_json(orient='records')
        resp['result'] = result
        resp['sUserId'] = get_data['sUserId'][0]
        write_log(log_path_exe, json.dumps(resp, ensure_ascii=False))

    except Exception, e:
        print "ERROR\n\n"
        resp['code'] = 1
        resp['msg'] = traceback.format_exc()
        logger.error(str(request) + resp['msg'])

    return json.dumps(resp, ensure_ascii=False)

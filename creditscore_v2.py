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


ios_clf1 = joblib.load('Model_file/Ios_lr_0_0412.model')
ios_clf2 = joblib.load('Model_file/Ios_lr_15_0412.model')
ios_clf3 = joblib.load('Model_file/Ios_lr_30_0412.model')
android_clf1 = joblib.load('Model_file/Android_lr_0_0412.model')
android_clf2 = joblib.load('Model_file/Android_lr_15_0412.model')
android_clf3 = joblib.load('Model_file/Android_lr_30_0412.model')

####配置变量名称
ios_columns = ["yunfeng_currentdueamount","yunfeng_historyoverduetimes","zdcy_score","yunfeng_historyloantimes","is_ios_11",
                "baidu_risk_score","phone_apply_fail_cnt","num_credit_cards","tongdun_cnt_apply_3m"]


android_columns = ["yunfeng_historyoverduetimes","yunfeng_historyloantimes","zdcy_score","contact_holiday","phone_apply_fail_cnt",
				"tongdun_cnt_apply_3m","yunfeng_currentdueamount","avg_call_time_6"]



creditscore_v2_Api = Blueprint('creditscore_v2_Api', __name__)

log_path = log_path + "/creditscore_v2_Api.log"
logger = getLogger('creditscore_v2_model')
handler = handlers.RotatingFileHandler(log_path,maxBytes=100 * 1024 * 1024,backupCount=5)
formatter = Formatter(log_formatter)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(20)


def write_log(log_path, result):
    f = open(log_path,"a+")
    f.write(result+'\n')
    f.close()



@creditscore_v2Api.route("/model_api/creditscore_v2/ios", methods=["POST"])
def get_result_ios():
    log_path_exe = mark_path + "/creditscore_v2.log." + time.strftime("%Y-%m-%d", time.localtime())
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    resp = {"Model_name":"creditscore_v2_ios","sUserId":[],"current_time": current_time,"msg": "ok", "code": 0, "input_data": [],"data_final": [],"reslut_detail":[], "result": 0}

    logger.info(
        'receive a  ios_creditscore_v2Api  request: {0}'.format(str(request)))
    try:
        ####获取数据

        input_data = request.form['input_data'].encode("utf-8")

        input_data = eval(input_data)

        ###解析数据
        get_data = pd.DataFrame(input_data, index=[0])

        ###数据处理
        if get_data['version_num'][0].split('.')[0] == '10':
            get_data['is_ios_10'] = 1
        else:
            get_data['is_ios_10'] = 0

        if get_data['version_num'][0].split('.')[0] == '11':
            get_data['is_ios_11'] = 1
        else:
            get_data['is_ios_11'] = 0

        #####选取入模型的指标
        data_final = get_data[ios_columns]

        #####加载模型预测

        result1 = int(ios_clf1.predict_proba(data_final)[:, 0] * 1000)
        result2 = int(ios_clf2.predict_proba(data_final)[:, 0] * 1000)
        result3 = int(ios_clf3.predict_proba(data_final)[:, 0] * 1000)

        model_score_threadhold = [784.733, 909.599, 932.26]


        if ((result1 >= model_score_threadhold[0]) & (result2 >= model_score_threadhold[1]) & (
                result3 >= model_score_threadhold[2])):
            result = 3
        else:
            result = -1

        #####结果保存
        resp['input_data'] = input_data
        resp['data_final'] = data_final.to_json(orient='records')
        resp['result'] = result
        resp['reslut_detail'] = model_score_threadhold
        resp['sUserId'] = get_data['sUserId'][0]
        write_log(log_path_exe,json.dumps(resp, ensure_ascii=False))

    except Exception, e:
        print "ERROR\n\n"
        resp['code'] = 1
        resp['msg'] = traceback.format_exc()
        logger.error(str(request) + resp['msg'])

    return json.dumps(resp, ensure_ascii=False)


######安卓API
@creditscore_v2_v2Api.route("/model_api/creditscore_v2/android", methods=["POST"])
def get_result_android():
    log_path_exe = mark_path + "/creditscore_v2.log." + time.strftime("%Y-%m-%d", time.localtime())
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    resp = {"Model_name":"creditscore_v2_android","sUserId":[],"current_time": current_time, "msg": "ok", "code": 0, "input_data": [], "data_final": [], "result": 0}

    logger.info(
        'receive a  android_creditscore_v2Api  request: {0}'.format(str(request)))
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

        result1 = int(ios_clf1.predict_proba(data_final)[:, 0] * 1000)
        result2 = int(ios_clf2.predict_proba(data_final)[:, 0] * 1000)
        result3 = int(ios_clf3.predict_proba(data_final)[:, 0] * 1000)

        model_score_threadhold = [695.514, 837.53, 868.789]

        if ((result1 >= model_score_threadhold[0]) & (result2 >= model_score_threadhold[1]) & (
                result3 >= model_score_threadhold[2])):
            result = 3
        else:
            result = -1

        #####结果保存
        resp['input_data'] = input_data
        resp['data_final'] = data_final.to_json(orient='records')
        resp['result'] = result
        resp['reslut_detail'] = model_score_threadhold
        resp['sUserId'] = get_data['sUserId'][0]
        write_log(log_path_exe, json.dumps(resp, ensure_ascii=False))

    except Exception, e:
        print "ERROR\n\n"
        resp['code'] = 1
        resp['msg'] = traceback.format_exc()
        logger.error(str(request) + resp['msg'])

    return json.dumps(resp, ensure_ascii=False)

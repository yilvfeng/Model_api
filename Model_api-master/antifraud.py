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
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (RandomTreesEmbedding, RandomForestClassifier,
                              GradientBoostingClassifier)
from sklearn.preprocessing import OneHotEncoder


reload(sys)
sys.setdefaultencoding('utf-8')

####配置模型目录
MODEL_PATH_IOS = "./Model_file/finalized_model_IOS.model"
MODEL_PATH_ANDROID = "./Model_file/finalized_model_Andr.model"

ios_clf = joblib.load(MODEL_PATH_IOS)
android_clf = joblib.load(MODEL_PATH_ANDROID)
####配置变量名称
ios_columns = ['yunfeng_currentdueamount','yunfeng_historyoverduetimes','tongdun_cnt_apply_3m',
'tongdun_cnt_apply_7day','cuishou_cnt','yunfeng_historyloantimes', 'D_version_num_11',
'night_activities_rate','user_login_cnt','dev_login_cnt','dev_ip_cnt','contact_early_morning','online_mons','device_city_cnt','D_zdcy_score_nag',
'D_zdcy_score_pos']


android_columns = ['yunfeng_currentdueamount','yunfeng_historyoverduetimes','tongdun_cnt_apply_3m', 'phone_apply_fail_cnt',
'tongdun_cnt_apply_7day','cuishou_cnt','yunfeng_historyloantimes','txl_call_rate','turn_off_rate', 'dev_login_interval_60s_cnt',
'version_num_7', 'isex', 'user_login_cnt','dev_login_cnt','dev_ip_cnt','contact_early_morning','online_mons','device_city_cnt',
                   'D_zdcy_score_pos']


antifraudApi = Blueprint('antifraudApi', __name__)

log_path = log_path + "/antifraudApi.log"
logger = getLogger('antifraud_model')
handler = handlers.RotatingFileHandler(log_path,maxBytes=100 * 1024 * 1024,backupCount=5)
formatter = Formatter(log_formatter)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(20)


def write_log(log_path, result):
    f = open(log_path,"a+")
    f.write(result+'\n')
    f.close()




@antifraudApi.route("/model_api/antifraud/ios", methods=["POST"])
def get_result_ios():
    log_path_exe = mark_path + "/antifraud.log." + time.strftime("%Y-%m-%d", time.localtime())
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    resp = {"Model_name":"antifraud_ios","sUserId":[],"current_time": current_time,"msg": "ok", "code": 0, "input_data": [],"data_final": [], "result": 0}

    logger.info(
        'receive a  ios_antifraudApi  request: {0}'.format(str(request)))
    try:
        ####获取数据

        input_data = request.form['input_data'].encode("utf-8")

        input_data = eval(input_data)

        ###解析数据
        get_data = pd.DataFrame(input_data, index = [0])


        ###数据处理
        if float(get_data['zdcy_score'][0]) <= 60:
            get_data['D_zdcy_score_nag'] = 1
        else :
            get_data['D_zdcy_score_nag'] = 0

        if float(get_data['zdcy_score'][0]) >= 72:
            get_data['D_zdcy_score_pos'] = 1
        else :
            get_data['D_zdcy_score_pos'] = 0

        if get_data['version_num'][0].split('.')[0]  == '11':
            get_data['D_version_num_11'] = 1
        else :
            get_data['D_version_num_11'] = 0

        if get_data['yunfeng_currentdueamount'][0] == '-1':
            get_data['yunfeng_currentdueamount'] = 0.0
        if get_data['yunfeng_historyoverduetimes'][0] == '-1':
            get_data['yunfeng_historyoverduetimes'] = 1.0
        if get_data['tongdun_cnt_apply_3m'][0] == '-1':
            get_data['tongdun_cnt_apply_3m'] = 30.0

        if get_data['tongdun_cnt_apply_7day'][0] == '-1':
            get_data['tongdun_cnt_apply_7day'] = 8.0
        if get_data['cuishou_cnt'][0] == '-1':
            get_data['cuishou_cnt'] = 1.0
        if get_data['yunfeng_historyloantimes'][0] == '-1':
            get_data['yunfeng_historyloantimes'] = 4.0

        if get_data['night_activities_rate'][0] == '-1':
            get_data['night_activities_rate'] = 10.24
        if get_data['user_login_cnt'][0] == '-1':
            get_data['user_login_cnt'] = 4.0
        if get_data['dev_login_cnt'][0] == '-1':
            get_data['dev_login_cnt'] = 11.0
        if get_data['dev_ip_cnt'][0] == '-1':
            get_data['dev_ip_cnt'] = 7.0
        if get_data['contact_early_morning'][0] == '-1':
            get_data['contact_early_morning'] = 39.0
        if get_data['online_mons'][0] == '-1':
            get_data['online_mons'] = 44.0
        if get_data['device_city_cnt'][0] == '-1':
            get_data['device_city_cnt'] = 1.0


        #####选取入模型的指标
        data_final = get_data[ios_columns]
        print data_final

        #####加载模型预测

        result = int(round((ios_clf.predict_proba(data_final)[0, 0] * 1000), 0))

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
@antifraudApi.route("/model_api/antifraud/android", methods=["POST"])
def get_result_android():
    log_path_exe = mark_path + "/antifraud.log." + time.strftime("%Y-%m-%d", time.localtime())
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    resp = {"Model_name":"antifraud_android","sUserId":[],"current_time": current_time, "msg": "ok", "code": 0, "input_data": [], "data_final": [], "result": 0}

    logger.info(
        'receive a  android_antifraudApi  request: {0}'.format(str(request)))
    try:
        ####获取数据

        input_data = request.form['input_data'].encode("utf-8")

        input_data = eval(input_data)

        ###解析数据
        get_data = pd.DataFrame(input_data, index = [0])

        ###数据处理

        if float(get_data['zdcy_score'][0]) <= 60:
            get_data['D_zdcy_score_nag'] = 1
        else:
            get_data['D_zdcy_score_nag'] = 0

        if float(get_data['zdcy_score'][0]) >= 72:
            get_data['D_zdcy_score_pos'] = 1
        else:
            get_data['D_zdcy_score_pos'] = 0

        if get_data['version_num'][0].split('.')[0] == '7':
            get_data['version_num_7'] = 1
        else :
            get_data['version_num_7'] = 0

        if get_data['yunfeng_currentdueamount'][0] == '-1':
            get_data['yunfeng_currentdueamount'] = 0.0

        if get_data['yunfeng_historyoverduetimes'][0] == '-1':
            get_data['yunfeng_historyoverduetimes'] = 1.0

        if get_data['tongdun_cnt_apply_3m'][0] == '-1':
            get_data['tongdun_cnt_apply_3m'] = 28.0


        if get_data['phone_apply_fail_cnt'][0] == '-1':
            get_data['phone_apply_fail_cnt'] = 0.0

        if get_data['tongdun_cnt_apply_7day'][0] == '-1':
            get_data['tongdun_cnt_apply_7day'] = 8.0

        if get_data['cuishou_cnt'][0] == '-1':
            get_data['cuishou_cnt'] = 1.0

        if get_data['yunfeng_historyloantimes'][0] == '-1':
            get_data['yunfeng_historyloantimes'] = 3.0

        if get_data['txl_call_rate'][0] == '-1':
            get_data['txl_call_rate'] = 0.3330

        if get_data['turn_off_rate'][0] == '-1':
            get_data['turn_off_rate'] = 0.0196

        if get_data['dev_login_interval_60s_cnt'][0] == '-1':
            get_data['dev_login_interval_60s_cnt'] = 0.00

        if get_data['version_num_7'][0] == '-1':
            get_data['version_num_7'] = 0.0

        if get_data['isex'][0] == '-1':
            get_data['isex'] = 0.0

        if get_data['user_login_cnt'][0] == '-1':
            get_data['user_login_cnt'] = 5.0

        if get_data['dev_login_cnt'][0] == '-1':
            get_data['dev_login_cnt'] = 7.0

        if get_data['dev_ip_cnt'][0] == '-1':
            get_data['dev_ip_cnt'] = 5.0

        if get_data['contact_early_morning'][0] == '-1':
            get_data['contact_early_morning'] = 23.0

        if get_data['online_mons'][0] == '-1':
            get_data['online_mons'] = 46.0

        if get_data['device_city_cnt'][0] == '-1':
            get_data['device_city_cnt'] = 1.0
        #####选取入模型的指标
        data_final = get_data[android_columns]


        #####加载模型预测

        result = int(round((android_clf.predict_proba(data_final)[0, 0] * 1000), 0))

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

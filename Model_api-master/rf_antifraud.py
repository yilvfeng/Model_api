# -*- coding: utf-8 -*-
import json
import time
import sys
import pandas as pd
import traceback
from flask import Flask, Blueprint
from flask import request
from settings import log_path, log_formatter
from logging import handlers, Formatter, getLogger
from sklearn.externals import joblib

startTime = time.time()


reload(sys)
sys.setdefaultencoding('utf-8')

####配置模型目录
MODEL_PATH = "/Users/wanghongkui/Documents/maiya_work/model/rf_antifraud.model"
clf = joblib.load(MODEL_PATH)


print "Load costs %d ms" % (int(round(time.time()*1000 - startTime*1000)))

####配置变量名称
x_columns = ['device_ip_cnt', 'yunfeng_historyloantimes', 'yunfeng_currentdueamount', 'yunfeng_currentoverduetimes', 'yunfeng_historyoverduetimes', 'user_isin_yq_30_contacts', 'txl_yq_cnt', 'tongdun_cnt_apply_3m', 'zdcy_score', 'night_activities_rate', 'tongdun_cnt_apply_7day', 'tongdun_cnt_apply_1m', 'regist_jk_apply_interval', 'online_mons', 'txl_call_rate', 'contact_num', 'linkman_phone_len_rate', 'linkman_phone_len', 'sage', 'linkman_phone_cnt']

rf_antifraudApi = Blueprint('rf_antifraudApi', __name__)
handler = handlers.RotatingFileHandler("./api_log/rf_antifraudApi.log",
                                       maxBytes=100 * 1024 * 1024,
                                       backupCount=5)
formatter = Formatter(log_formatter)
handler.setFormatter(formatter)
logger = getLogger('model_api')
logger.addHandler(handler)
logger.setLevel(20)




@rf_antifraudApi.route("/model_api/rf_antifraud", methods=["POST"])
def get_result():
    resp = {"msg": "ok", "code": 0, "input_data": [], "result": [], "cost_ms": []}

    logger.info(
        'receive a  rf_antifraudApi  request: {0}'.format(str(request)))

    beginTime = time.time()
    try:
        ####获取数据

        input_data = request.form['input_data'].encode("utf-8")

        input_data = eval(input_data)

        ###解析数据
        get_data = pd.DataFrame(input_data, index = [0])


        #####加载模型预测

        result = round(clf.predict_proba(get_data)[0,1]*100, 2)


        resp['input_data'].append(input_data)
        resp['result'].append(result)

    except Exception, e:
        print "ERROR\n\n"
        resp['code'] = 1
        resp['msg'] = traceback.format_exc()
        logger.error(str(request) + resp['msg'])


    resp['cost_ms'] = int(round(time.time()*1000 - beginTime*1000))
    return json.dumps(resp, ensure_ascii=False)



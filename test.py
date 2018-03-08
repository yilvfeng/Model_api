import json
import pandas as pd
from flask import Flask, Blueprint
from flask import request
from settings import log_path, log_formatter
from logging import handlers, Formatter, getLogger
from sklearn.externals import joblib
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (RandomTreesEmbedding, RandomForestClassifier,
                              GradientBoostingClassifier)
from sklearn.preprocessing import OneHotEncoder

# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

#sys.setdefaultencoding('utf-8')

MODEL_PATH_IOS = "./Model_file/lr_5.pkl"
ios_clf = joblib.load(MODEL_PATH_IOS)
ios_columns = ['version_num_p',  'sage_p',
       'call_linkman_num_r', 'txl_call_rate_p', 'cuishou_cnt_p',
       'tongdun_cnt_apply_7day_p', 'user_txl_active_r', 
       'contact_early_morning_pp', 'num_loan_p',
       'night_activities_rate_pp', 'num_house_r']


edu = Blueprint('edu', __name__)
handler = handlers.RotatingFileHandler("./edu.log",
                                       maxBytes=100 * 1024 * 1024,
                                       backupCount=5)
formatter = Formatter(log_formatter)
handler.setFormatter(formatter)
logger = getLogger('model_api')
logger.addHandler(handler)
logger.setLevel(20)


@edu.route("/model_api/edu", methods=["POST"])  
def get_result_ios():
    resp = {"msg": "ok", "code": 0, "input_data": [],"data_final": [], "result": 0}

    logger.info(
        'receive a  ios_antifraudApi  request: {0}'.format(str(request)))
    print("ok1")
    input_data = request.form['input_data'].encode("utf-8")
    print(input_data)
    input_data = eval(input_data)
    ###解析数据
    get_data = pd.DataFrame(input_data, index = [0])
    #####选取入模型的指标
    data_final = get_data[ios_columns]
    #####加载模型预测
    result = int(round((ios_clf.predict_proba(data_final)[0, 0] * 1000), 0))
    #####结果保存
    resp['input_data'] = input_data
    resp['data_final'] = data_final.to_json(orient='records')
    resp['result'] = result
    return json.dumps(resp, ensure_ascii=False)































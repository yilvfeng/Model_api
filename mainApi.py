#!/usr/bin/env python

from flask import Flask
import sys
import os
from antifraud import antifraudApi
from creditscore import creditscoreApi
from xjcard_antifraud import xjcard_antifraudApi
from xjcard_creditscore import xjcard_creditscoreApi
from creditscore_v2 import creditscore_v2_Api
# from test import edu


app = Flask(__name__)
app.register_blueprint(antifraudApi)
app.register_blueprint(creditscoreApi)
app.register_blueprint(xjcard_antifraudApi)
app.register_blueprint(xjcard_creditscoreApi)
app.register_blueprint(creditscore_v2_Api)
# app.register_blueprint(edu)


if __name__ == '__main__':
    port = int(os.getenv("API_PORT", 5061))
    app.run(host='0.0.0.0', port=port, threaded=True, debug=True)
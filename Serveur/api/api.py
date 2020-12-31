import json

import flask
from flask import jsonify, make_response
from Serveur.sensor_manager import ARCHIVE_LOG_PATH
from Serveur.api import service as service
import re
from Serveur.sensor_manager import SensorAllLogsFileModel as salfm

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>ADS API</h1><p>Welcome to ADS API, here you can find and manage all sensors logs registered.</p>"


@app.route('/allDataDay/<date>', methods=['GET'])
def allDataDay(date):
    # Check pattern of the date given for avoiding error
    pattern = re.compile("[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]$")
    if pattern.match(date):
        pathFile = ARCHIVE_LOG_PATH + date + '/all_logs.csv'
        try:
            allLogsFileModel = salfm.SensorAllLogsFileModel(pathFile)
            result = allLogsFileModel.content.to_json(orient="index")
            parsed = json.loads(result)
            response = make_response(parsed, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception:
            response = make_response(jsonify("File not found"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
    else:
        response = make_response(jsonify("Date not given in the right format"), 400)
        response.headers["Content-Type"] = "application/json"
        return response


@app.route('/getDateLogs', methods=['GET'])
def getDateLogs():
    listDateLogs = service.listDateLogs()
    response = make_response(jsonify(listDateLogs), 200)
    response.headers["Content-Type"] = "application/json"
    return response


def run():
    app.run()

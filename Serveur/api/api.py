import flask
import json
import re
from flask import jsonify, make_response
from Serveur.sensor_manager import ARCHIVE_LOG_PATH
from Serveur.api import service as service
from Serveur.sensor_manager import SensorAllLogsFileModel as salfm
from Serveur.sensor_manager import SensorLogFileModel as slfm

app = flask.Flask(__name__)
app.config["DEBUG"] = True


# Api homepage
@app.route('/', methods=['GET'])
def home():
    return "<h1>ADS API</h1><p>Welcome to ADS API, here you can find and manage all sensors logs registered.</p>"


# Ping -> Check if API is working
@app.route('/ping', methods=['GET'])
def ping():
    response = make_response("pong", 200)
    response.headers["Content-Type"] = "application/json"
    return response


# Get or delete content of all_logs.csv from the date given
@app.route('/allDataDay/<date>', methods=['GET', 'DELETE'])
def allDataDay(date):
    # Check pattern of the date given for avoiding error
    pattern = re.compile("[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]$")
    if pattern.match(date):
        if flask.request.method == 'GET':
            pathFile = ARCHIVE_LOG_PATH + date + '/all_logs.csv'
            try:
                allLogsFileModel = salfm.SensorAllLogsFileModel(pathFile)
                result = allLogsFileModel.content.to_json(orient="table")
                parsed = json.loads(result)
                response = make_response(parsed, 200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception:
                response = make_response(jsonify("File not found"), 400)
                response.headers["Content-Type"] = "application/json"
                return response
        if flask.request.method == 'DELETE':
            directoryToDelete = ARCHIVE_LOG_PATH + date
            try:
                service.deleteDirectory(directoryToDelete)
                response = make_response(jsonify("Logs from " + date + " deleted"), 204)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception:
                response = make_response(jsonify("Error during deletion"), 400)
                response.headers["Content-Type"] = "application/json"
                return response
    else:
        response = make_response(jsonify("Date not given in the right format"), 400)
        response.headers["Content-Type"] = "application/json"
        return response


# Get or delete data from a sensor at the date given
@app.route('/dataFromSensor/<sensor>/<date>', methods=['GET', 'DELETE'])
def getDataFromSensor(sensor, date):
    # Check pattern of the date given for avoiding error
    patternDate = re.compile("[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]$")
    if patternDate.match(date):
        fileName = sensor + "__" + date + ".csv"
        pathFile = ARCHIVE_LOG_PATH + date + "/" + fileName
        if flask.request.method == 'GET':
            try:
                logFileModel = slfm.SensorLogFileModel(pathFile)
                result = logFileModel.content.to_json(orient="index")
                parsed = json.loads(result)
                response = make_response(parsed, 200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception:
                response = make_response(jsonify("File not found"), 400)
                response.headers["Content-Type"] = "application/json"
                return response
        if flask.request.method == 'DELETE':
            try:
                service.deleteFile(pathFile)
                response = make_response(jsonify("Logs of " + sensor + " from " + date + " are deleted"), 204)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception:
                response = make_response(jsonify("Error during deletion"), 400)
                response.headers["Content-Type"] = "application/json"
                return response
    else:
        response = make_response(jsonify("Date not given in the right format"), 400)
        response.headers["Content-Type"] = "application/json"
        return response


# Get all files found from a sensor
@app.route('/allFilesFromASensor/<sensor>', methods=['GET'])
def allFilesFromASensor(sensor):
    if flask.request.method == 'GET':
        try:
            listDateLogs = service.listSensorLog(sensor)
            response = make_response(jsonify(listDateLogs), 200)
            response.headers["Content-Type"] = "application/json"
        except Exception:
            response = make_response(jsonify("Unknown error during searchin all logs from a sensor"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        return response


@app.route('/getDateLogs', methods=['GET'])
def getDateLogs():
    listDateLogs = service.listDateLogs()
    response = make_response(jsonify(listDateLogs), 200)
    response.headers["Content-Type"] = "application/json"
    return response


def run():
    app.run(host='0.0.0.0')

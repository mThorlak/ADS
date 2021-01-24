import flask
import re
import pandas as pd
from flask import jsonify, make_response
from Serveur.sensor_manager import ARCHIVE_LOG_PATH
from Serveur.rules_manager import CONFIG_SENSORS_PATH, WHITE_LIST_PATH, BLACK_LIST_PATH
from Serveur.api import service as service
from Serveur.sensor_manager import SensorAllLogsFileModel as salfm
from Serveur.sensor_manager import SensorLogFileModel as slfm
from Serveur.rules_manager import SensorConfigModel as scm
from Serveur.rules_manager.list import listModel as bwl

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
                result = allLogsFileModel.content.to_json(orient='records')
                response = make_response(result, 200)
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
                response = make_response(jsonify("Logs from " + date + " deleted"), 200)
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
                result = logFileModel.content.to_json(orient='records')
                response = make_response(result, 200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception:
                response = make_response(jsonify("File not found"), 400)
                response.headers["Content-Type"] = "application/json"
                return response
        if flask.request.method == 'DELETE':
            try:
                service.deleteFile(pathFile)
                response = make_response(jsonify("Logs of " + sensor + " from " + date + " are deleted"), 200)
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
            response = make_response(jsonify("Unknown error during searchinf all logs from a sensor"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        return response


@app.route('/getDateLogs', methods=['GET'])
def getDateLogs():
    listDateLogs = service.listDateLogs()
    response = make_response(jsonify(listDateLogs), 200)
    response.headers["Content-Type"] = "application/json"
    return response


# Manage sensors_config.csv
@app.route('/configSensor', methods=['GET', 'POST', 'PUT'])
def configSensor():
    # Get method
    if flask.request.method == 'GET':
        try:
            sensorConfigFile = scm.SensorConfigModel()
            result = sensorConfigFile.content.to_json(orient='records')
            response = make_response(result, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception:
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response

    # Post method
    if flask.request.method == 'POST':
        try:
            sensorToAdd = flask.request.get_json()
        except Exception:
            response = make_response(jsonify("Error, bad request"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        sensorToAdd = {
            'Name': str(sensorToAdd['Name']).lower(),
            'Mac_Address': sensorToAdd['Mac_Address'],
            'Priority': sensorToAdd['Priority']
        }
        dataFrame = pd.DataFrame(pd.json_normalize(sensorToAdd))
        try:
            open(CONFIG_SENSORS_PATH)
            dataFrame.to_csv(CONFIG_SENSORS_PATH, mode='a', sep=',', header=False, index=False)
            sensorConfigFile = scm.SensorConfigModel()
            result = sensorConfigFile.content.to_json(orient='records')
            response = make_response(result, 201)
            response.headers["Content-Type"] = "application/json"
            return response
        # Manage case where the file does not exists, so we add headers into the file
        except Exception:
            dataFrame.to_csv(CONFIG_SENSORS_PATH, mode='a', sep=',', header=True, index=False)
            sensorConfigFile = scm.SensorConfigModel()
            result = sensorConfigFile.content.to_json(orient='records')
            response = make_response(result, 201)
            response.headers["Content-Type"] = "application/json"
            return response

    # PUT method
    if flask.request.method == 'PUT':
        try:
            sensorToAdd = flask.request.get_json()
        except Exception:
            response = make_response(jsonify("Error, bad request"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        sensorToAdd = {
            'Name': str(sensorToAdd['Name']).lower(),
            'Mac_Address': sensorToAdd['Mac_Address'],
            'Priority': sensorToAdd['Priority']
        }
        dataFrame = pd.DataFrame(pd.json_normalize(sensorToAdd))
        try:
            open(CONFIG_SENSORS_PATH)
            sensorConfigFile = scm.SensorConfigModel()
            sensorConfigFile.content = sensorConfigFile.content[
                sensorConfigFile.content.Name != sensorToAdd['Name']]
            sensorConfigFile.content.to_csv(CONFIG_SENSORS_PATH, index=False)
            dataFrame.to_csv(CONFIG_SENSORS_PATH, mode='a', sep=',', header=False, index=False)
            response = make_response(sensorToAdd['Name'] + " sensors updated", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        # Manage case where the file does not exists, so we add headers into the file
        except Exception:
            response = make_response("Error during the update of a sensor in config_sensor file", 201)
            response.headers["Content-Type"] = "application/json"
            return response


# Delete sensor from sensors_config.csv
@app.route('/configSensor/<SensorName>', methods=['DELETE'])
def deleteSensorFromConfigSensor(SensorName):
    # Delete method
    if flask.request.method == 'DELETE':
        try:
            sensorNameToDelete = str(SensorName).lower()
            sensorConfigFile = scm.SensorConfigModel()
            sensorConfigFile.content = sensorConfigFile.content[
                sensorConfigFile.content.Name != sensorNameToDelete]
            sensorConfigFile.content.to_csv(CONFIG_SENSORS_PATH, index=False)
            result = sensorConfigFile.content.to_json(orient='records')
            response = make_response(result, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception:
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response


# Manage whiteList.csv
@app.route('/whiteList', methods=['GET', 'POST'])
def whiteList():
    # Get method
    if flask.request.method == 'GET':
        try:
            whiteListFile = bwl.ListModel()
            result = whiteListFile.contentWhiteList.to_json(orient='records')
            response = make_response(result, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception:
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response

    # Post method
    if flask.request.method == 'POST':
        try:
            sensorToAdd = flask.request.get_json()
        except Exception:
            response = make_response(jsonify("Error, bad request"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        sensorToAdd = {
            'Mac_Address': sensorToAdd['Mac_Address']
        }
        dataFrame = pd.DataFrame(pd.json_normalize(sensorToAdd))
        try:
            open(WHITE_LIST_PATH)
            whiteListFile = bwl.ListModel()
            if sensorToAdd['Mac_Address'] in whiteListFile.contentWhiteList['Mac_Address'].values:
                pass
            else:
                dataFrame.to_csv(WHITE_LIST_PATH, mode='a', sep=',', header=False, index=False)
            response = make_response(sensorToAdd['Mac_Address'] + " added", 201)
            response.headers["Content-Type"] = "application/json"
            return response
        # Manage case where the file does not exists, so we add headers into the file
        except Exception:
            dataFrame.to_csv(WHITE_LIST_PATH, mode='a', sep=',', header=True, index=False)
            whiteListFile = bwl.ListModel()
            result = whiteListFile.contentWhiteList.to_json(orient='records')
            response = make_response(result, 201)
            response.headers["Content-Type"] = "application/json"
            return response


# Delete sensor from sensors_config.csv
@app.route('/whiteList/<MacAddress>', methods=['DELETE'])
def deleteFromWhiteList(MacAddress):
    # Delete method
    if flask.request.method == 'DELETE':
        try:
            macAddressToDelete = str(MacAddress)
            whiteListFile = bwl.ListModel()
            whiteListFile.contentWhiteList = whiteListFile.contentWhiteList[
                whiteListFile.contentWhiteList.Mac_Address != macAddressToDelete]
            whiteListFile.contentWhiteList.to_csv(WHITE_LIST_PATH, index=False)
            response = make_response(macAddressToDelete + " deleted from white list", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception:
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response


# Manage blacklist.csv
@app.route('/blackList', methods=['GET', 'POST'])
def blackList():
    # Get method
    if flask.request.method == 'GET':
        try:
            blackListFile = bwl.ListModel()
            result = blackListFile.contentBlackList.to_json(orient='records')
            response = make_response(result, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception:
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response

    # Post method
    if flask.request.method == 'POST':
        try:
            sensorToAdd = flask.request.get_json()
        except Exception:
            response = make_response(jsonify("Error, bad request"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        sensorToAdd = {
            'Mac_Address': sensorToAdd['Mac_Address']
        }
        dataFrame = pd.DataFrame(pd.json_normalize(sensorToAdd))
        try:
            open(BLACK_LIST_PATH)
            blackListFile = bwl.ListModel()
            if sensorToAdd['Mac_Address'] in blackListFile.contentBlackList['Mac_Address'].values:
                pass
            else:
                dataFrame.to_csv(BLACK_LIST_PATH, mode='a', sep=',', header=False, index=False)
            response = make_response(sensorToAdd['Mac_Address'] + " added", 201)
            response.headers["Content-Type"] = "application/json"
            return response
        # Manage case where the file does not exists, so we add headers into the file
        except Exception:
            dataFrame.to_csv(BLACK_LIST_PATH, mode='a', sep=',', header=True, index=False)
            blackListFile = bwl.ListModel()
            result = blackListFile.contentBlackList.to_json(orient='records')
            response = make_response(result, 201)
            response.headers["Content-Type"] = "application/json"
            return response


# Delete sensor from blacklist.csv
@app.route('/blackList/<MacAddress>', methods=['DELETE'])
def deleteFromBlackList(MacAddress):
    # Delete method
    if flask.request.method == 'DELETE':
        try:
            macAddressToDelete = str(MacAddress)
            blackListFile = bwl.ListModel()
            blackListFile.contentBlackList = blackListFile.contentBlackList[
                blackListFile.contentBlackList.Mac_Address != macAddressToDelete]
            blackListFile.contentBlackList.to_csv(BLACK_LIST_PATH, index=False)
            response = make_response(macAddressToDelete + " deleted from black list", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception:
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response


@app.route('/test', methods=['GET'])
def test():
    # Delete method
    if flask.request.method == 'GET':
        try:
            response = make_response("ok", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception:
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response


def run():
    app.run(host='0.0.0.0')

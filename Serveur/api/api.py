import flask
import re
import logging.config
import pandas as pd
from flask import jsonify, make_response
from Serveur.api import LOG_CONFIG_PATH
from Serveur.sensor_manager import ARCHIVE_LOG_PATH
from Serveur.rules_manager import CONFIG_SENSORS_PATH, WHITE_LIST_PATH, BLACK_LIST_PATH
from Serveur.api import service as service
from Serveur.sensor_manager import SensorAllLogsFileModel as salfm
from Serveur.sensor_manager import SensorLogFileModel as slfm
from Serveur.rules_manager import SensorConfigModel as scm
from Serveur.rules_manager.list import listModel as bwl
from Serveur.rules_manager import RssiManager as RssiManager
from Serveur.sensor_manager.SensorModel import SensorModel

app = flask.Flask(__name__)
app.config["DEBUG"] = True
logging.config.fileConfig(LOG_CONFIG_PATH)
logger = logging.getLogger('API')


# Api homepage
@app.route('/', methods=['GET'])
def home():
    return "<h1>ADS API</h1><p>Welcome to ADS API, here you can find and manage all sensors logs registered.</p>"


# Ping -> Check if API is working
@app.route('/ping', methods=['GET'])
def ping():
    try:
        response = make_response("pong", 200)
        response.headers["Content-Type"] = "application/json"
        logger.info('health-check working')
        return response
    except Exception as e:
        logger.error('GET ping')
        logger.error(e)
        response = make_response(jsonify("Error on ping request"), 400)
        response.headers["Content-Type"] = "application/json"
        return response


# Receive logs from a sensor, convert it to csv format for processing
@app.route('/sensor', methods=['POST'])
def insertSensor():
    if flask.request.method == 'POST':
        request_data = flask.request.get_json()
        sensor_name = request_data["Sensor_Name"]
        sensor_date = request_data["Date_Sensor"]
        content = request_data["Content"]
        try:
            sensor = SensorModel(sensor_name, sensor_date, content)
            logger.info('Sensor information received')
            logger.info(sensor.getSensorDescription())
            logger.info(sensor.getContent())
            sensor.convertIntoCsvLogFile()
            response = make_response("Log inserted", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('POST insert sensor')
            logger.error(e)
            response = make_response(jsonify("Bad format request"), 400)
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
                logger.info('Generating all_data_day model...')
                logger.info(allLogsFileModel.getProperty())
                logger.info(allLogsFileModel.getContent())
                result = allLogsFileModel.content.to_json(orient='records')
                response = make_response(result, 200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception as e:
                logger.error('GET all data day ')
                logger.error(e)
                response = make_response(jsonify("File not found"), 400)
                response.headers["Content-Type"] = "application/json"
                return response
        if flask.request.method == 'DELETE':
            directoryToDelete = ARCHIVE_LOG_PATH + date
            try:
                logger.info('Deleting all_data_day from given date :' + + date)
                service.deleteDirectory(directoryToDelete)
                response = make_response(jsonify("Logs from " + date + " deleted"), 200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception as e:
                logger.error('DELETE all data ')
                logger.error(e)
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
                logger.info('Generating sensor-log-file model...')
                logger.info(logFileModel.getProperty())
                logger.info(logFileModel.getProperty())
                result = logFileModel.content.to_json(orient='records')
                response = make_response(result, 200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception as e:
                logger.error('GET data from sensor')
                logger.error(e)
                response = make_response(jsonify("File not found"), 400)
                response.headers["Content-Type"] = "application/json"
                return response
        if flask.request.method == 'DELETE':
            try:
                service.deleteFile(pathFile)
                logger.info('Delete following file : ' + pathFile)
                response = make_response(jsonify("Logs of " + sensor + " from " + date + " are deleted"), 200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception as e:
                logger.error('DELETE data from sensor')
                logger.error(e)
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
            logger.info('Generating all files from a sensor....')
            logger.info(listDateLogs)
            response = make_response(jsonify(listDateLogs), 200)
            response.headers["Content-Type"] = "application/json"
        except Exception as e:
            logger.error('GET all files from a sensor')
            logger.error(e)
            response = make_response(jsonify("Unknown error during searchinf all logs from a sensor"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        return response


# Get all dates where sensor logs are stored
@app.route('/getDateLogs', methods=['GET'])
def getDateLogs():
    try:
        listDateLogs = service.listDateLogs()
        logger.info('Generating date list where sensor logs are found....')
        logger.info(listDateLogs)
        response = make_response(jsonify(listDateLogs), 200)
        response.headers["Content-Type"] = "application/json"
        return response
    except Exception as e:
        logger.error('GET list of date where logs are found')
        logger.error(e)
        response = make_response(jsonify("Error, cannot find date"), 400)
        response.headers["Content-Type"] = "application/json"
        return response


# Manage sensors_config.csv
@app.route('/configSensor', methods=['GET', 'POST', 'PUT'])
def configSensor():
    if flask.request.method == 'GET':
        try:
            sensorConfigFile = scm.SensorConfigModel()
            logger.info('Generating sensor config file....')
            logger.info(sensorConfigFile.getProperty())
            logger.info(sensorConfigFile.getContent())
            result = sensorConfigFile.content.to_json(orient='records')
            response = make_response(result, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('GET config sensor file')
            logger.error(e)
            response = make_response(jsonify(Exception), 500)
            response.headers["Content-Type"] = "application/json"
            return response

    if flask.request.method == 'POST':
        try:
            sensorToAdd = flask.request.get_json()
        except Exception as e:
            logger.error('POST config sensor file')
            logger.error(e)
            response = make_response(jsonify("Error, bad request"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        sensorToAdd = {
            'Name': str(sensorToAdd['Name']).lower(),
            'Mac_Address': sensorToAdd['Mac_Address'],
            'Priority': sensorToAdd['Priority'],
            'Room_Description': sensorToAdd['Room_Description'],
            'Range': None
        }
        dataFrame = pd.DataFrame(pd.json_normalize(sensorToAdd))
        try:
            open(CONFIG_SENSORS_PATH)
            dataFrame.to_csv(CONFIG_SENSORS_PATH, mode='a', sep=',', header=False, index=False)
            sensorConfigFile = scm.SensorConfigModel()
            logger.info('Modifying sensor config file....')
            logger.info(sensorConfigFile.getProperty())
            logger.info(sensorConfigFile.getContent())
            result = sensorConfigFile.content.to_json(orient='records')
            response = make_response(result, 201)
            response.headers["Content-Type"] = "application/json"
            return response
        # Manage case where the file does not exists, so we add headers into the file
        except Exception as e:
            dataFrame.to_csv(CONFIG_SENSORS_PATH, mode='a', sep=',', header=True, index=False)
            sensorConfigFile = scm.SensorConfigModel()
            result = sensorConfigFile.content.to_json(orient='records')
            logger.info('Creating sensor config file....')
            logger.info(sensorConfigFile.getProperty())
            logger.info(sensorConfigFile.getContent())
            response = make_response(result, 201)
            response.headers["Content-Type"] = "application/json"
            return response

    if flask.request.method == 'PUT':
        try:
            sensorToAdd = flask.request.get_json()
        except Exception as e:
            logger.error('PUT config sensor file')
            logger.error(e)
            response = make_response(jsonify("Error, bad request"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        sensorToAdd = {
            'Name': str(sensorToAdd['Name']).lower(),
            'Mac_Address': sensorToAdd['Mac_Address'],
            'Priority': sensorToAdd['Priority'],
            'Room_Description': sensorToAdd['Room_Description'],
            'Range': sensorToAdd['Range']
        }
        dataFrame = pd.DataFrame(pd.json_normalize(sensorToAdd))
        try:
            open(CONFIG_SENSORS_PATH)
            sensorConfigFile = scm.SensorConfigModel()
            sensorConfigFile.content = sensorConfigFile.content[
                sensorConfigFile.content.Name != sensorToAdd['Name']]
            sensorConfigFile.content.to_csv(CONFIG_SENSORS_PATH, index=False)
            dataFrame.to_csv(CONFIG_SENSORS_PATH, mode='a', sep=',', header=False, index=False)
            logger.info('Modifying sensor config file....')
            logger.info(sensorConfigFile.getProperty())
            logger.info(sensorConfigFile.getContent())
            response = make_response(sensorToAdd['Name'] + " sensors updated", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        # Manage case where the file does not exists
        except Exception as e:
            logger.error('PUT config sensor file')
            logger.error(e)
            response = make_response("File does not exists", 500)
            response.headers["Content-Type"] = "application/json"
            return response


# Manage sensors_config range
@app.route('/configSensor/range', methods=['PUT'])
def addRangeConfigSensor():
    if flask.request.method == 'PUT':
        try:
            rangeToAdd = flask.request.get_json()
            rangeToAdd = {
                'Name': str(rangeToAdd['Name']).lower(),
                'Max_Range': rangeToAdd['Max_Range']
            }
        except Exception as e:
            logger.error('POST RSSI config sensor')
            logger.error(e)
            response = make_response(jsonify("Error, bad request"), 400)
            response.headers["Content-Type"] = "application/json"
            return response
        try:
            sensorConfigFile = scm.SensorConfigModel()
            if rangeToAdd['Name'] in sensorConfigFile.content['Name'].values:
                sensorConfigFile.content.at[sensorConfigFile.content['Name'] == rangeToAdd['Name'], 'Max_Range'] = \
                    rangeToAdd['Max_Range']
                logger.info('Modifying config for sensor :')
                logger.info(sensorConfigFile.content.to_json)
                sensorConfigFile.content.to_csv(CONFIG_SENSORS_PATH, mode='w', sep=',', header=True, index=False)
            result = sensorConfigFile.content.to_json(orient='records')
            response = make_response(result, 201)
            response.headers["Content-Type"] = "application/json"
            return response
        # Manage case where the file does not exists
        except Exception as e:
            logger.error('Add range config file....')
            logger.error(e)
            response = make_response("File does not exist", 400)
            response.headers["Content-Type"] = "application/json"
            return response


# Flush range for a specified sensor
@app.route('/configSensor/range/<SensorName>', methods=['DELETE'])
def deleteRangeConfigSensor(SensorName):
    if flask.request.method == 'DELETE':
        try:
            sensorConfigFile = scm.SensorConfigModel()
            SensorName = str(SensorName).lower()
            if SensorName in sensorConfigFile.content['Name'].values:
                sensorConfigFile.content.at[sensorConfigFile.content['Name'] == SensorName, 'Max_Range'] = None
                logger.info('Deleting range for specified config sensor... :')
                logger.info(sensorConfigFile.content.to_json)
                sensorConfigFile.content.to_csv(CONFIG_SENSORS_PATH, mode='w', sep=',', header=True, index=False)
            result = sensorConfigFile.content.to_json(orient='records')
            response = make_response(result, 201)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('DELETE range sensor from the config sensor file')
            logger.error(e)
            response = make_response(jsonify(Exception), 400)
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
            logger.info('Deleting sensor from the config file....')
            logger.info(sensorConfigFile.getProperty())
            logger.info(sensorConfigFile.getContent())
            response = make_response(result, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('DELETE sensor from the config sensor file')
            logger.error(e)
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
            logger.info('Generating whitelist file....')
            logger.info(whiteListFile.contentWhiteList())
            response = make_response(result, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('GET whitelist sensor file')
            logger.error(e)
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response

    # Post method
    if flask.request.method == 'POST':
        try:
            sensorToAdd = flask.request.get_json()
        except Exception as e:
            logger.error('POST whitelist sensor file')
            logger.error(e)
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
            logger.info('Modifying whitelist file....')
            logger.info(whiteListFile.contentWhiteList())
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
            logger.info('Modifying whitelist file....')
            logger.info(whiteListFile.contentWhiteList())
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
            logger.info('Deleting sensor from the whitelist file....')
            logger.info(whiteListFile.contentWhiteList())
            response = make_response(macAddressToDelete + " deleted from white list", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('DELETE sensor from whitelist sensor file')
            logger.error(e)
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
            logger.info('Generating blacklist file....')
            logger.info(blackListFile.contentBlackList())
            response = make_response(result, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('GET blacklist sensor file')
            logger.error(e)
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response

    # Post method
    if flask.request.method == 'POST':
        try:
            sensorToAdd = flask.request.get_json()
        except Exception as e:
            logger.error('POST blacklist sensor file')
            logger.error(e)
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
            logger.info('Modifying blacklist file....')
            logger.info(blackListFile.contentBlackList())
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
            logger.info('Creating blacklist file....')
            logger.info(blackListFile.contentBlackList())
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
            logger.info('Deleting sensor from the blacklist file....')
            logger.info(blackListFile.contentWhiteList())
            response = make_response(macAddressToDelete + " deleted from black list", 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('DELETE sensor from blackilistr sensor file')
            logger.error(e)
            response = make_response(jsonify(Exception), 400)
            response.headers["Content-Type"] = "application/json"
            return response


# Search logs by mac_address and date
@app.route('/searchLogs/<date>/<mac_address>', methods=['GET'])
def listLogsByDateAndMacAddress(date, mac_address):
    # Check pattern of the date given for avoiding error
    pattern = re.compile("[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]$")
    if pattern.match(date):
        if flask.request.method == 'GET':
            try:
                logger.info('Searching logs by mac address and date....')
                logsForSpecifiedDateAndMacAddress = service.getLogsByDateAndMacAddress(date, mac_address)
                logger.info(logsForSpecifiedDateAndMacAddress)
                result = logsForSpecifiedDateAndMacAddress.to_json(orient='records')
                response = make_response(result, 200)
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception as e:
                logger.error('Search logs')
                logger.error(e)
                response = make_response(jsonify("Logs not found"), 400)
                response.headers["Content-Type"] = "application/json"
                return response


# Locate device
@app.route('/locate/<date>/<mac_address>', methods=['GET'])
def locateDevice(date, mac_address):
    # Check pattern of the date given for avoiding error
    if flask.request.method == 'GET':
        try:
            logger.info('Locate mac address ....')
            result = RssiManager.run(mac_address, date)
            if result is None:
                response = make_response("No location found", 200)
                response.headers["Content-Type"] = "application/json"
            else:
                response = make_response(result, 200)
                response.headers["Content-Type"] = "application/json"
            return response
        except Exception as e:
            logger.error('Locate logs')
            logger.error(e)
            response = make_response(jsonify("Logs not found"), 400)
            response.headers["Content-Type"] = "application/json"
            return response


def run():
    app.run(host='0.0.0.0')

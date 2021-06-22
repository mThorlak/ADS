import os as os
import shutil
from Serveur.sensor_manager import ARCHIVE_LOG_PATH
from Serveur.sensor_manager import SensorAllLogsFileModel as salfm


# Get all the log dates by listing the name of the archiv_logs's subdirectories
def listDateLogs():
    directoryList = []
    for root, dirs, files in os.walk(ARCHIVE_LOG_PATH):
        directoryList.append(dirs)
    # [0] for returning only subdirectories
    return directoryList[0]


# List of logs from a sensor given in parameter
def listSensorLog(sensorName):
    filesList = []
    for root, dirs, files in os.walk(ARCHIVE_LOG_PATH):
        for file in files:
            if sensorName + "__" in file:
                filesList.append(file)
    # [0] for returning only subdirectories
    return filesList


# Delete directory given in parameters
def deleteDirectory(directoryPath):
    try:
        shutil.rmtree(directoryPath)
    except OSError as e:
        print("Error: %s : %s" % (directoryPath, e.strerror))


# Delete file
def deleteFile(fileName):
    try:
        os.remove(fileName)
    except OSError as e:
        print("Error: %s : %s" % (fileName, e.strerror))


# Create file
def createFile(fileName):
    try:
        open(fileName, 'w').close()
    except OSError as e:
        print("Error: %s : %s" % (fileName, e.strerror))

# Get all the logs from a specified date
def getAllLogsByDate(date):
    pathFile = ARCHIVE_LOG_PATH + date + '/all_logs.csv'
    return salfm.SensorAllLogsFileModel(pathFile)


# List all logs for a specified Mac address and date
def getLogsByDateAndMacAddress(date, mac_address):
    allLogs = getAllLogsByDate(date)
    logsMacAddress = allLogs.getLogsForMacAddress(mac_address)
    return logsMacAddress
